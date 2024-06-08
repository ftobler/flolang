#!flolang

fn crc8_update(int data, int polynomial=0x07) int:
    crc ^= data
    for int _ in 0..8:
        if crc & 0x80:
            crc = (crc << 1) ^ polynomial
        else:
            crc = crc << 1
        crc &= 0xFF  # Ensure CRC remains 8-bit
    return crc

fn main():
    let int init_value = 0x00
    let mut int crc = init_value
    for int i in 1..4:
        crc = crc8_update(i)

    # print result
    print(crc)

main()