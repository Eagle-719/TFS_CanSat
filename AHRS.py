import math

class MahonyAHRS:
    def __init__(self, sample_period=0.01, kp=1.0, ki=0.0):
        """
        Initialize the Mahony filter.

        :param sample_period: Time between updates (in seconds)
        :param kp: Proportional gain
        :param ki: Integral gain (set to 0 to disable integral feedback)
        """
        self.sample_period = sample_period
        self.kp = kp
        self.ki = ki

        # Quaternion representing the estimated orientation (initialized to no rotation)
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        # Integral error terms for gyroscope bias estimation
        self.exInt = 0.0
        self.eyInt = 0.0
        self.ezInt = 0.0

    def update(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        """
        Update the AHRS algorithm with new sensor readings.
        Gyroscope units: rad/s.
        Accelerometer units: g (normalized before use).
        Magnetometer units: any units (will be normalized).
        """
        # Normalize the accelerometer measurement
        norm = math.sqrt(ax * ax + ay * ay + az * az)
        if norm == 0:
            return  # invalid reading, cannot update
        ax /= norm
        ay /= norm
        az /= norm

        # Normalize the magnetometer measurement
        norm = math.sqrt(mx * mx + my * my + mz * mz)
        if norm == 0:
            return  # invalid reading, cannot update
        mx /= norm
        my /= norm
        mz /= norm

        # Short name local variable for readability
        q0 = self.q0
        q1 = self.q1
        q2 = self.q2
        q3 = self.q3

        # Reference direction of Earth's magnetic field
        hx = 2.0 * mx * (0.5 - q2 * q2 - q3 * q3) + \
             2.0 * my * (q1 * q2 - q0 * q3) + \
             2.0 * mz * (q1 * q3 + q0 * q2)
        hy = 2.0 * mx * (q1 * q2 + q0 * q3) + \
             2.0 * my * (0.5 - q1 * q1 - q3 * q3) + \
             2.0 * mz * (q2 * q3 - q0 * q1)
        bx = math.sqrt((hx * hx) + (hy * hy))
        bz = 2.0 * mx * (q1 * q3 - q0 * q2) + \
             2.0 * my * (q2 * q3 + q0 * q1) + \
             2.0 * mz * (0.5 - q1 * q1 - q2 * q2)

        # Estimated direction of gravity (from quaternion)
        vx = 2.0 * (q1 * q3 - q0 * q2)
        vy = 2.0 * (q0 * q1 + q2 * q3)
        vz = q0 * q0 - q1 * q1 - q2 * q2 + q3 * q3

        # Estimated direction of the magnetic field (in the body frame)
        wx = 2.0 * bx * (0.5 - q2 * q2 - q3 * q3) + \
             2.0 * bz * (q1 * q3 - q0 * q2)
        wy = 2.0 * bx * (q1 * q2 - q0 * q3) + \
             2.0 * bz * (q0 * q1 + q2 * q3)
        wz = 2.0 * bx * (q0 * q2 + q1 * q3) + \
             2.0 * bz * (0.5 - q1 * q1 - q2 * q2)

        # Error is the sum of the cross products between estimated and measured directions
        ex = (ay * vz - az * vy) + (my * wz - mz * wy)
        ey = (az * vx - ax * vz) + (mz * wx - mx * wz)
        ez = (ax * vy - ay * vx) + (mx * wy - my * wx)

        # Apply integral feedback if enabled
        self.exInt += ex * self.ki * self.sample_period
        self.eyInt += ey * self.ki * self.sample_period
        self.ezInt += ez * self.ki * self.sample_period

        # Adjust gyroscope measurements with feedback
        gx += self.kp * ex + self.exInt
        gy += self.kp * ey + self.eyInt
        gz += self.kp * ez + self.ezInt

        # Integrate rate of change of quaternion: q_dot = 0.5 * q ⨂ [0, gx, gy, gz]
        dq0 = 0.5 * (-q1 * gx - q2 * gy - q3 * gz)
        dq1 = 0.5 * ( q0 * gx + q2 * gz - q3 * gy)
        dq2 = 0.5 * ( q0 * gy - q1 * gz + q3 * gx)
        dq3 = 0.5 * ( q0 * gz + q1 * gy - q2 * gx)

        # Update quaternion using Euler integration
        q0 += dq0 * self.sample_period
        q1 += dq1 * self.sample_period
        q2 += dq2 * self.sample_period
        q3 += dq3 * self.sample_period

        # Normalize quaternion to prevent error accumulation
        norm = math.sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3)
        q0 /= norm
        q1 /= norm
        q2 /= norm
        q3 /= norm

        # Store updated quaternion
        self.q0 = q0
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3

    def get_quaternion(self):
        """Return the current orientation as a quaternion tuple (q0, q1, q2, q3)."""
        return (self.q0, self.q1, self.q2, self.q3)

    def get_euler(self):
        """
        Return the current orientation as Euler angles (roll, pitch, yaw) in radians.
        Uses the following conversions:
          roll  = atan2(2(q0q1 + q2q3), 1 - 2(q1^2 + q2^2))
          pitch = asin(2(q0q2 - q3q1))
          yaw   = atan2(2(q0q3 + q1q2), 1 - 2(q2^2 + q3^2))
        """
        q0, q1, q2, q3 = self.q0, self.q1, self.q2, self.q3

        # Roll (x-axis rotation)
        sinr_cosp = 2.0 * (q0 * q1 + q2 * q3)
        cosr_cosp = 1.0 - 2.0 * (q1 * q1 + q2 * q2)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2.0 * (q0 * q2 - q3 * q1)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2.0 * (q0 * q3 + q1 * q2)
        cosy_cosp = 1.0 - 2.0 * (q2 * q2 + q3 * q3)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return (roll, pitch, yaw)

# --- Example Usage ---
# You must implement your own functions to read the sensor values
# For example, using I2C to interface with the MPU6050 and magnetometer.

def read_hw290(i2c):
    # Addresses for devices on the HW290 module
    mpu_addr = 0x68      # MPU6050 (accelerometer & gyroscope)
    qmc_addr = 0x0D      # QMC5883L (magnetometer)

    # --- MPU6050 Setup ---
    # Wake up MPU6050 by writing 0 to the power management register (0x6B)
    i2c.writeto_mem(mpu_addr, 0x6B, b'\x00')
    # Enable I2C bypass mode so that the magnetometer can be accessed directly
    i2c.writeto_mem(mpu_addr, 0x37, b'\x02')

    # Read 14 bytes from MPU6050 starting at register 0x3B:
    # Accel: XH, XL, YH, YL, ZH, ZL
    # Temp: 2 bytes (ignored here)
    # Gyro: XH, XL, YH, YL, ZH, ZL
    mpu_data = i2c.readfrom_mem(mpu_addr, 0x3B, 14)

    # Helper function to convert a 16-bit value from two's complement
    def twos_compl(val):
        return -((0xFFFF - val) + 1) if val & 0x8000 else val

    # --- Accelerometer (MPU6050) ---
    # MPU6050 defaults to ±2g with a sensitivity of 16384 LSB/g.
    raw_ax = twos_compl((mpu_data[0] << 8) | mpu_data[1])
    raw_ay = twos_compl((mpu_data[2] << 8) | mpu_data[3])
    raw_az = twos_compl((mpu_data[4] << 8) | mpu_data[5])
    ax = raw_ax / 16384.0
    ay = raw_ay / 16384.0
    az = raw_az / 16384.0

    # --- Gyroscope (MPU6050) ---
    # MPU6050 defaults to ±250°/s with a sensitivity of 131 LSB/(°/s).
    raw_gx = twos_compl((mpu_data[8]  << 8) | mpu_data[9])
    raw_gy = twos_compl((mpu_data[10] << 8) | mpu_data[11])
    raw_gz = twos_compl((mpu_data[12] << 8) | mpu_data[13])
    # Convert from °/s to rad/s
    gx = raw_gx / 131.0 * (math.pi / 180)
    gy = raw_gy / 131.0 * (math.pi / 180)
    gz = raw_gz / 131.0 * (math.pi / 180)

    # --- QMC5883L (Magnetometer) Setup ---
    # Perform a soft reset (if supported) by writing 0x01 to register 0x0B
    i2c.writeto_mem(qmc_addr, 0x0B, b'\x01')
    # Configure the magnetometer by writing to register 0x09.
    # Here 0x1D sets: 512 oversampling, 8G range, 200Hz output data rate, and continuous measurement mode.
    i2c.writeto_mem(qmc_addr, 0x09, b'\x1D')
    # Wait briefly to allow the settings to take effect
    time.sleep_ms(10)

    # Read 6 bytes from QMC5883L starting at register 0x00.
    # Note: QMC5883L outputs data in little-endian order:
    # X_L, X_H, Y_L, Y_H, Z_L, Z_H
    mag_data = i2c.readfrom_mem(qmc_addr, 0x00, 6)
    # Combine the two bytes for each axis (little-endian) and convert to signed values.
    raw_mx = (mag_data[1] << 8) | mag_data[0]
    raw_my = (mag_data[3] << 8) | mag_data[2]
    raw_mz = (mag_data[5] << 8) | mag_data[4]
    if raw_mx & 0x8000:
        raw_mx = -((0xFFFF - raw_mx) + 1)
    if raw_my & 0x8000:
        raw_my = -((0xFFFF - raw_my) + 1)
    if raw_mz & 0x8000:
        raw_mz = -((0xFFFF - raw_mz) + 1)

    # --- Magnetometer Conversion ---
    # For QMC5883L in 8G mode, the sensitivity is typically about 1200 LSB/gauss.
    mx = raw_mx / 1200.0
    my = raw_my / 1200.0
    mz = raw_mz / 1200.0

    # Return sensor values: gyroscope (rad/s), accelerometer (g), magnetometer (gauss)
    return gx, gy, gz, ax, ay, az, mx, my, mz
