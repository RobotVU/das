import struct
import json

SIZE_BYTES = 4
STRUCT_IDENTIFIER = ">I"  # big-endian unsigned short (2 bytes)


def pack(data):
    """
    Wraps a message which is to be sent via a TCP socket according to the protocol:
    big-endian 2bytes message length + message in bytes
    :param data: the data to be sent
    :return: the prepared message as a byte string
    """
    data_bytes = data.encode('utf8')
    size = struct.pack(STRUCT_IDENTIFIER, len(data_bytes))
    return b"".join([size, data_bytes])


def read_message(socket):
    """
    Receives a message from a TCP socket of various length.
    The first to bytes in big-endian order signal the size of the current message to receive.
    :param socket: the socket to receive from
    :return: the full received message as a utf8 string
    """

    # read 2 bytes to determine size of message
    size_data = read_bytes_from_socket(socket, SIZE_BYTES)
    # get message size from struct
    message_size = struct.unpack(STRUCT_IDENTIFIER, size_data)[0]

    # read actual message
    data = read_bytes_from_socket(socket, message_size)
    return data.decode('utf8')


def read_bytes_from_socket(socket, size):
    """
    Reads #size bytes from the socket
    :param socket: the socket to receive from
    :param size: the amount of bytes to read
    :return:
    """
    total_len = 0
    total_data = []
    recv_size = size

    # read #size bytes from socket
    while total_len < size:
        try:
            # note: socket.recv can return before receiving full size
            sock_data = socket.recv(recv_size)
        except:
            raise TCPConnectionError("Socket Closed")

        # if empty -> connection is closing
        if not sock_data:
            raise TCPConnectionError("Connection error while reading data.")
        else:
            total_data.append(sock_data)
            # calculate total_len from all chunks in total_data
            total_len = sum([len(i) for i in total_data])

            # adjust receive size to not receive too much data (e.g. from the next message)
            recv_size = size - total_len

    return b"".join(total_data)


def send_udp_message(socket, address, type, data=None):
    """
    Sens a UDP message via the socket to the given address with type and data set in JSON.
    :param socket: the socket to send the message
    :param address: the address to send the message to
    :param type: the message type
    :param data: the message data
    :return:
    """
    if data:
        data = json.dumps({"type": type, "payload": data})
    else:
        data = json.dumps({"type": type})
    socket.sendto(data.encode('utf-8'), address)


def read_udp_message(socket):
    """
    Reads a UDP message from the socket and unpacks it.
    :param socket: the socket to receive from
    :return: json decoded message and address (host, port) as a tuple
    """
    data, address = socket.recvfrom(4096)
    data = data.decode('utf-8')
    return json.loads(data), address


class TCPConnectionError(Exception):
    def __init__(self, msg="Error with the connection"):
        super(TCPConnectionError, self).__init__(msg)
