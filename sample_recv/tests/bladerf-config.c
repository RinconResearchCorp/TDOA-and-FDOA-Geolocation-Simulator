#include <inttypes.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include <math.h>
#include <time.h>
#include <stdio.h>
#include <assert.h>
#include <libbladeRF.h>
#include <bladeRF2.h>
#include <zmq.h>

int16_t *init_sync_rx(struct bladerf *dev, int16_t num_samples, bladerf_format format,
              bladerf_channel_layout channel_layout)
{
    int status = -1;

    /* "User" buffer that we read samples into and do work on, and its
     * associated size, in units of samples. Recall that for the
     * SC16Q11 format (native to the ADCs), one sample = two int16_t values.
     *
     * When using the bladerf_sync_* functions, the buffer size isn't
     * restricted to multiples of any particular size.
     *
     * The value for `num_samples` has no major restrictions here, while the
     * `buffer_size` below must be a multiple of 1024.
     */
    int16_t *samples;

    /* These items configure the underlying async stream used by the the sync
     * interface. The "buffer" here refers to those used internally by worker
     * threads, not the `samples` buffer above. */
    const unsigned int num_buffers   = 16;
    const unsigned int num_transfers = 8;
    const unsigned int timeout_ms    = 1000;
    const unsigned int buffer_size   = 2048;

    samples = malloc(num_samples * 2 * sizeof(int16_t));
    if (samples == NULL) {
        perror("malloc");
        goto error;
    }

    /** [sync_config] */

    /* Configure the device's RX for use with the sync interface.
     * SC16 Q11 samples *with* metadata are used. */
    status = bladerf_sync_config(dev, channel_layout,
                                 format, num_buffers,
                                 buffer_size, num_transfers, timeout_ms);
    if (status != 0) {
        fprintf(stderr, "Failed to configure RX sync interface: %s\n",
                bladerf_strerror(status));

        goto error;
    }

    /** [sync_config] */

    /* We must always enable the RX front end *after* calling
     * bladerf_sync_config(), and *before* attempting to RX samples via
     * bladerf_sync_rx(). */
    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(0), true);
    if (status != 0) {
        fprintf(stderr, "Failed to enable RX(0): %s\n", bladerf_strerror(status));
        goto error;
    }

    if (channel_layout == BLADERF_RX_X2) {
        status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(1), true);
        if (status != 0) {
            fprintf(stderr, "Failed to enable RX(1): %s\n", bladerf_strerror(status));
            goto error;
        }
    }

    status = 0;

error:
    if (status != 0) {
        free(samples);
        samples = NULL;
    }

    return samples;
}

int deinit_bladerf(struct bladerf *dev, int16_t *samples)
{
    int status = bladerf_enable_module(dev, BLADERF_RX, false);
    if (status != 0) {
        fprintf(stderr, "Failed to disable RX: %s\n", bladerf_strerror(status));
    }

    /* Deinitialize and free resources */
    free(samples);
    bladerf_close(dev);
    return 0;
}

void my_free(void *data, void *hint) {
    free(data);
}

int receive_with_time(struct bladerf *dev, int16_t *samples, unsigned int samples_len, unsigned int rx_count, unsigned int timeout_ms, void *publisher)
{
    int status = 0;
    struct bladerf_metadata meta;
    unsigned int i;


    /* Perform a read immediately, and have the bladerf_sync_rx function
    * provide the timestamp of the read samples */

    memset(&meta, 0, sizeof(meta));
    meta.flags = BLADERF_META_FLAG_RX_NOW;

    /* Receive samples and do work on them */
    int count = 0;
    while(count < 10) {
        status = bladerf_sync_rx(dev, samples, samples_len, &meta, timeout_ms);
        if (status != 0) {
            fprintf(stderr, "RX \"now\" failed: %s\n\n", bladerf_strerror(status));
        } else if (meta.status & BLADERF_META_STATUS_OVERRUN) {
            fprintf(stderr, "Overrun detected. %u valid samples were read.\n", meta.actual_count);
        } else {
            printf("RX'd %u samples at t=0x%016" PRIx64 "\n", meta.actual_count, meta.timestamp);
            uint64_t timestamp = (uint64_t) meta.timestamp;
            zmq_msg_t msg1;
            int rc = zmq_msg_init_size(&msg1, samples_len * sizeof(int16_t) * 2);
            memcpy(zmq_msg_data(&msg1), samples, samples_len * sizeof(int16_t) * 2);
            if (rc != 0) {
                fprintf(stderr, "Failed to initialize message: %s\n", zmq_strerror(rc));
                return -1;
            }

            // send the message
            if (zmq_msg_send(&msg1, publisher, ZMQ_SNDMORE) == -1) {
                fprintf(stderr, "Failed to send message: %s\n", zmq_strerror(errno));
                zmq_msg_close(&msg1);
                return -1;
            }

            zmq_msg_t msg2;
            rc = zmq_msg_init_size(&msg2, sizeof(uint64_t));
            memcpy(zmq_msg_data(&msg2), &timestamp, sizeof(uint64_t));
            if (rc != 0) {
                fprintf(stderr, "Failed to initialize message: %s\n", zmq_strerror(rc));
                return -1;
            }
            if (zmq_msg_send(&msg2, publisher, 0) == -1) {
                fprintf(stderr, "Failed to send message: %s\n", zmq_strerror(errno));
                zmq_msg_close(&msg2);
                return -1;
            }

            fflush(stdout);
            count++;
        }
    }
    return status;
}

struct bladerf *init_bladerf(struct bladerf *dev) {
    int status;
    status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(0), 1090000000);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX frequency: %s\n",
                bladerf_strerror(status));
        goto out;
    } else {
        printf("RX frequency: %u Hz\n", 1090000000);
    }

    status = bladerf_set_sample_rate(dev, BLADERF_CHANNEL_RX(0),
                                     2000000, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX sample rate: %s\n",
                bladerf_strerror(status));
        goto out;
    } else {
        printf("RX samplerate: %u sps\n", 2000000);
    }

    /* Not sure on bandwidth

    status = bladerf_set_bandwidth(dev, BLADERF_CHANNEL_RX(0),
                                   2000000, NULL);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX bandwidth: %s\n",
                bladerf_strerror(status));
        goto out;
    } else {
        printf("RX bandwidth: %u Hz\n", 2000000);
    }

    */

    status = bladerf_set_gain(dev, BLADERF_CHANNEL_RX(0), 50);
    if (status != 0) {
        fprintf(stderr, "Failed to set RX gain: %s\n",
                bladerf_strerror(status));
        goto out;
    } else {
        printf("RX gain: %d\n", 50);
    }

    out:
    if (status != 0) {
        bladerf_close(dev);
        return NULL;
    } else {
        return dev;
    }
}

int main(int argc, char *argv[]) {
    struct bladerf *dev = NULL;
    struct bladerf_devinfo dev_info;
    unsigned int num_samples = 4096;
 
    /* Initialize the information used to identify the desired device
    * to all wildcard (i.e., "any device") values */

    bladerf_init_devinfo(&dev_info);

 
    int status = bladerf_open_with_devinfo(&dev, &dev_info);
    if (status != 0) {
        fprintf(stderr, "Unable to open device: %s\n",
        bladerf_strerror(status));
        return 0;
    }

    dev = init_bladerf(dev);
    if (!dev) {
        fprintf(stderr, "Failed to initialize device\n");
        return 0;
    }

    /* Initialize ZeroMQ connection */
    
    //int port = 5555;
    void *context = zmq_ctx_new();
    void *publisher = zmq_socket(context, ZMQ_PUB);
    char *address = "tcp://127.0.0.1:5555";
    assert(zmq_bind(publisher, address) == 0);


    /* Initialize BladeRF connection, samples buffer */

    int16_t* samples = init_sync_rx(dev, num_samples, BLADERF_FORMAT_SC16_Q11_META, BLADERF_RX_X1, 10240);
    if (samples != NULL) {
        printf("Press ENTER to send the message: ");
        getchar();
        status = receive_with_time(dev, samples, num_samples, 1, 0, publisher); // receive samples
    } else {
        fprintf(stderr, "Failed to initialize samples buffer\n");
    }

    /* Deinitialize BladeRF connection, samples buffer */

    deinit_bladerf(dev, samples);

    /* Close ZMQ connection */

    zmq_close(publisher);
    zmq_ctx_destroy(context);
    printf("ZMQ Connection closed\n");

    return 0;
}