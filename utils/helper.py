# Utility functions used by both client and server.

def get_packet_header(payload_len, psecret, step, sid):
    """
    Returns 12-byte packet header based on the given payload length,
    previous secret, step number, and last 3 digits of student id.
    """
    print("Got packet header!")