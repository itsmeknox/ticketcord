import time
import threading

class SnowflakeGenerator:
    def __init__(self, epoch_start: int = 1420070400000):
        """
        Initialize the Snowflake generator.
        :param epoch_start: Custom epoch start time in milliseconds. Default is Discord's epoch (2015-01-01).
        """
        self.epoch_start = epoch_start
        self.last_timestamp = -1  # Tracks the last generated timestamp
        self.sequence = 0  # Incremental counter for the same millisecond
        self.lock = threading.Lock()  # Ensure thread safety

    def _current_timestamp(self) -> int:
        """Returns the current timestamp in milliseconds."""
        return int(time.time() * 1000)

    def next_id(self) -> int:
        """
        Generate the next unique ID (Snowflake).
        :return: A unique 64-bit integer.
        """
        with self.lock:  # Ensure thread safety
            current_timestamp = self._current_timestamp()

            if current_timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate ID.")

            if current_timestamp == self.last_timestamp:
                # Increment sequence within the same millisecond
                self.sequence = (self.sequence + 1) & 0xFFF  # Limit to 12 bits (4096 max)
                if self.sequence == 0:
                    # Sequence overflow, wait for the next millisecond
                    while current_timestamp <= self.last_timestamp:
                        current_timestamp = self._current_timestamp()
            else:
                # New millisecond, reset sequence
                self.sequence = 0

            self.last_timestamp = current_timestamp

            # Construct the Snowflake
            snowflake_id = ((current_timestamp - self.epoch_start) << 22) | (self.sequence)

            return snowflake_id

generator = SnowflakeGenerator()

generate_unique_id = generator.next_id