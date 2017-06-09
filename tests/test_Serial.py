from raspibot.Serial import AttinyProtocol, InvalidResponseException

import pytest

ALIVE = b'\x01'

ENCODERS_RIGHT = b'\x02'
ENCODERS_LEFT = b'\x03'
ENCODERS_BOTH = b'\x04'

ACK = b'\x10'
NAK = b'\x14'

SET_BOTH_MOTORS = b'\x2D'

MOTOR_MIN = -127
MOTOR_MAX = 127
MOTOR_ZERO = 0

# as signed byte values:
BYTES_MOTOR_MIN = MOTOR_MIN.to_bytes(1, 'little', signed=True)
BYTES_MOTOR_MAX = MOTOR_MAX.to_bytes(1, 'little', signed=True)
BYTES_MOTOR_ZERO = MOTOR_ZERO.to_bytes(1, 'little', signed=True)

INVALID_RESPONSE = b'\x23'

class MockSerial:

    def __init__(self, bytes):
        self._bytes = bytes
        self._position = 0
        self.received = b''

    def write(self, bytes):
        self.received += bytes

    def read(self, count):
        try:
            return self._bytes[self._position:self._position+count]
            self._position += count
        except IndexError:
            return b''


def test_get_encoders():
    left, right = 0, 65535
    encoder_bytes = left.to_bytes(2, 'little') + right.to_bytes(2, 'little')
    serial = MockSerial(encoder_bytes)
    
    attiny = AttinyProtocol(serial)
    result = attiny.get_encoders()
    
    assert serial.received == ENCODERS_BOTH
    
    # use it as a tuple
    assert result == (left, right)
    
    # access tuple fields by index
    assert result[0] == left
    assert result[1] == right
    
    # access tuple fields by name
    assert result.left == left
    assert result.right == right
    
def test_get_left_encoder():
    value = 43690
    encoder_bytes = value.to_bytes(2, 'little')
    serial = MockSerial(encoder_bytes)
    
    attiny = AttinyProtocol(serial)
    result = attiny.get_left_encoder()
    
    assert serial.received == ENCODERS_LEFT
    assert result == value
    
def test_get_right_encoder():
    value = 21845
    encoder_bytes = value.to_bytes(2, 'little')
    serial = MockSerial(encoder_bytes)
    
    attiny = AttinyProtocol(serial)
    result = attiny.get_right_encoder()
    
    assert serial.received == ENCODERS_RIGHT
    assert result == value
    
def test_alive_ack():
    # send out an ACK byte
    serial = MockSerial(ACK)
    
    attiny = AttinyProtocol(serial)
    result = attiny.alive()
    
    assert serial.received == ALIVE
    assert result == True
    
def test_alive_nak():
    # send out an NAK byte
    serial = MockSerial(NAK)
    
    attiny = AttinyProtocol(serial)
    result = attiny.alive()
    
    assert serial.received == ALIVE
    assert result == False
    
def test_alive_undefined():
    # send out something that is neither an ACK or a NAK byte
    serial = MockSerial(INVALID_RESPONSE)
    
    attiny = AttinyProtocol(serial)
    with pytest.raises(InvalidResponseException):
        attiny.alive()

    assert serial.received == ALIVE
    
def test_set_both_motors():
    serial = MockSerial(ACK)
    
    left = MOTOR_MIN
    left_bytes = BYTES_MOTOR_MIN
    
    right = MOTOR_MAX
    right_bytes = BYTES_MOTOR_MAX
    
    attiny = AttinyProtocol(serial)
    attiny.set_motors(left, right)
    
    assert len(serial.received) == 3
    assert serial.received[0] == SET_BOTH_MOTORS
    assert serial.received[1] == left_bytes
    assert serial.received[2] == right_bytes
    
def test_set_both_motors2():
    serial = MockSerial(ACK)
    
    left = MOTOR_MAX
    left_bytes = BYTES_MOTOR_MAX
    
    right = MOTOR_MIN
    right_bytes = BYTES_MOTOR_MIN
    
    attiny = AttinyProtocol(serial)
    attiny.set_motors(left, right)
    
    assert len(serial.received) == 3
    assert serial.received[0] == SET_BOTH_MOTORS
    assert serial.received[1] == left_bytes
    assert serial.received[2] == right_bytes
    
def test_set_both_motors_zero():
    serial = MockSerial(ACK)
    
    left = MOTOR_ZERO
    left_bytes = BYTES_MOTOR_ZERO
    
    right = MOTOR_ZERO
    right_bytes = BYTES_MOTOR_ZERO
    
    attiny = AttinyProtocol(serial)
    result = attiny.set_motors(left, right)
    
    assert len(serial.received) == 3
    assert serial.received[0] == SET_BOTH_MOTORS
    assert serial.received[1] == left_bytes
    assert serial.received[2] == right_bytes
    
    assert result == True
    
# flake8: noqa
