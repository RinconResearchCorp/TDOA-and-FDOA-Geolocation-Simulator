#include <zmq.h>
#include <inttypes.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <math.h>
#include <stdio.h>
#include <assert.h>


int main(int argc, char *argv[])
{
    void *context = zmq_ctx_new();
    void *subscriber = zmq_socket(context, ZMQ_SUB);
    int rc = zmq_connect(subscriber, "tcp://127.0.0.1:5001");
    assert(rc == 0);
    rc = zmq_setsockopt(subscriber, ZMQ_SUBSCRIBE, "", 0);
    assert(rc == 0);

    zmq_msg_t msg1;
    rc = zmq_msg_init (&msg1);
    assert (rc == 0);
    /* Block until a message is available to be received from socket */
    while (1) {
        rc = zmq_msg_recv (&msg1, subscriber, 0);
        if (rc == -1) {
            printf("Failed to receive message: %s\n", zmq_strerror(errno));
            return -1;
        }
        printf("%s\n", (char *)zmq_msg_data(&msg1));
    }
    zmq_msg_close (&msg1);

    zmq_close(subscriber);
    zmq_ctx_destroy(context);

    return 0;
}
