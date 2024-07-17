#include <inttypes.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <math.h>
#include <stdio.h>
#include <assert.h>
#include <libbladeRF.h>
#include <bladeRF2.h>
#include <zmq.h>

pthread_t recv_thread;
pthread_mutex_t queue_access;
pthread_cond_t data_ready;

typedef struct Message {
    uint64_t timestamp;
    int16_t *samples;
    struct Message *next;
} Message;

typedef struct Queue {
    Message *head;
    Message *tail;
} Queue;

int destroy_list(Queue *queue)
{
    Message *current = queue->head;
    while (current != NULL)
    {
        Message *next = current->next;
        free(current->samples);
        free(current);
        current = next;
    }
    return 0;
}

int process_samples(Queue *queue, uint16_t *mag_lookup)
{
    while (1)
    {
        while (queue->head == NULL)
        {
            pthread_cond_wait(&data_ready, &queue_access);
        }
        pthread_mutex_lock(&queue_access);
        Message *message = queue->head;
        if (queue->head == queue->tail)
        {
            queue->head = NULL;
            queue->tail = NULL;
        }
        else
        {
            queue->head = queue->head->next;
        }
        pthread_mutex_unlock(&queue_access);
        demodulator(message, mag_lookup);
    }
}

int recv_message(void *subscriber, Queue *queue)
{
    zmq_msg_t msg1;
    int rc = zmq_msg_init (&msg1);
    assert (rc == 0);
    /* Block until a message is available to be received from socket */
    rc = zmq_msg_recv (&msg1, subscriber, 0);
    if (rc == -1) {
        printf("Failed to receive message: %s\n", zmq_strerror(errno));
        return -1;
    }
    // FIX NEED TWO MESSAGES
    printf("Received message 1\n");
    int16_t *data = malloc(4096 * sizeof(int16_t) * 2);
    if (!data)
    {
        printf("Failed to allocate memory for message\n");
        return -1;
    }
    memcpy(data, zmq_msg_data(&msg1), 4096 * sizeof(int16_t) * 2);
    zmq_msg_close (&msg1);
    
    zmq_msg_t msg2;
    rc = zmq_msg_init (&msg2);
    assert (rc == 0);
    /* Block until a message is available to be received from socket */
    rc = zmq_msg_recv (&msg2, subscriber, 0);
    if (rc == -1) {
        printf("Failed to receive message: %s\n", zmq_strerror(errno));
        return -1;
    }

    printf("Received message 2\n");

    Message *message = malloc(sizeof(Message));
    if (!message)
    {
        free(data);
        printf("Failed to allocate memory for message\n");
        return -1;
    }

    message->samples = data;
    message->timestamp = *(uint64_t *)zmq_msg_data(&msg2);

    zmq_msg_close (&msg2);
    pthread_mutex_lock(&queue_access);
    /* Add to the queue */
    if (queue->head == NULL) {
        queue->head = message;
        queue->tail = message;
    } else {
        message->next = NULL;
        queue->tail->next = message;
        queue->tail = message;
    }
    pthread_cond_signal(&data_ready);
    pthread_mutex_unlock(&queue_access);
    printf("%d\n", message->timestamp);
}

uint16_t *compute_mag_vector(int16_t *samples, uint16_t *mag_lookup)
{
    uint16_t *mag_vector = malloc(4096 * sizeof(uint16_t));
    for (int16_t j = 0; j < 4096 * 2; j+=2){
        int i = p[j] - 127;
        int q = p[j + 1] - 127;

        if (i < 0) i = -i;
        if (q < 0) q = -q;
        mag_vector[j/2] = mag_lookup[i*129 + q];
    }
    return mag_vector;
}

int demodulator(Message *message, uint16_t *mag_lookup) {
    uint16_t *mag_vector = compute_mag_vector(message->samples, mag_lookup);

    free(mag_vector);
    free(message->samples);
    free(message);
}


int main(int argc, char *argv[])
{
    void *context = zmq_ctx_new();
    void *subscriber = zmq_socket(context, ZMQ_SUB);
    int rc = zmq_connect(subscriber, "tcp://127.0.0.1:5555");
    assert(rc == 0);
    rc = zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "", 0);
    assert(rc == 0);

    void *msg;
    int counter = 0;

    Queue *queue = malloc(sizeof(Queue));
    if (!queue)
    {
        printf("Failed to allocate memory for queue\n");
        return -1;
    }
    queue->head = NULL;

    uint16_t *mag_lookup = malloc(129*129*2);
    if (!mag_lookup)
    {
        free(queue);
        printf("Failed to allocate memory for mag_lookup\n");
        return -1;
    }
    for (int i = 0; i <= 128; i++) {
        for (int q = 0; q <= 128; q++) {
            mag_lookup[i*129+q] = round(sqrt(i*i+q*q)*360);
        }
    }

    pthread_create(&recv_thread, NULL, recv_message, queue);

    process_samples(queue, mag_lookup);

    free(mag_lookup);
    destroy_list(queue);

    zmq_close(subscriber);
    zmq_ctx_destroy(context);

    return 0;
}

