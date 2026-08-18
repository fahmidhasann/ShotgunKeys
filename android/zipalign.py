#!/usr/bin/env python3
"""
Custom pure-Python ZIP aligner for Android APKs.
Aligns uncompressed zip entries to 4-byte boundaries according to Android APK spec.
"""
import sys
import struct
import zipfile

def align_apk(input_path, output_path, alignment=4):
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        in_zip = zipfile.ZipFile(f_in, 'r')
        entries = []

        for item in in_zip.infolist():
            data = in_zip.read(item.filename)
            entries.append((item, data))

        cd_entries = []

        for item, data in entries:
            local_header_offset = f_out.tell()
            filename_bytes = item.filename.encode('utf-8')
            extra = item.extra or b''

            # If uncompressed, calculate padding so data starts on alignment boundary
            if item.compress_type == 0:
                header_size = 30 + len(filename_bytes) + len(extra)
                data_offset = local_header_offset + header_size
                remainder = data_offset % alignment
                if remainder != 0:
                    padding = alignment - remainder
                    # Append null padding to extra field
                    extra += b'\x00' * padding

            # Write Local File Header
            # Local header signature 0x04034b50
            f_out.write(b'PK\x03\x04')
            f_out.write(struct.pack('<H', item.create_version if hasattr(item, 'create_version') else 20))
            f_out.write(struct.pack('<H', item.flag_bits))
            f_out.write(struct.pack('<H', item.compress_type))
            
            # DOS time/date
            dostime = (item.date_time[3] << 11) | (item.date_time[4] << 5) | (item.date_time[5] // 2)
            dosdate = ((item.date_time[0] - 1980) << 9) | (item.date_time[1] << 5) | item.date_time[2]
            f_out.write(struct.pack('<HH', dostime, dosdate))

            f_out.write(struct.pack('<III', item.CRC, item.compress_size, item.file_size))
            f_out.write(struct.pack('<HH', len(filename_bytes), len(extra)))
            f_out.write(filename_bytes)
            f_out.write(extra)

            # Write file data
            f_out.write(data)

            cd_entries.append((item, filename_bytes, extra, local_header_offset))

        # Central Directory
        cd_offset = f_out.tell()
        for item, filename_bytes, extra, local_header_offset in cd_entries:
            f_out.write(b'PK\x01\x02')
            f_out.write(struct.pack('<H', item.create_version if hasattr(item, 'create_version') else 20))
            f_out.write(struct.pack('<H', item.extract_version if hasattr(item, 'extract_version') else 20))
            f_out.write(struct.pack('<H', item.flag_bits))
            f_out.write(struct.pack('<H', item.compress_type))

            dostime = (item.date_time[3] << 11) | (item.date_time[4] << 5) | (item.date_time[5] // 2)
            dosdate = ((item.date_time[0] - 1980) << 9) | (item.date_time[1] << 5) | item.date_time[2]
            f_out.write(struct.pack('<HH', dostime, dosdate))

            f_out.write(struct.pack('<III', item.CRC, item.compress_size, item.file_size))
            f_out.write(struct.pack('<HHH', len(filename_bytes), len(extra), len(item.comment or b'')))
            f_out.write(struct.pack('<HHII', 0, 0, 0, local_header_offset))
            f_out.write(filename_bytes)
            f_out.write(extra)
            f_out.write(item.comment or b'')

        cd_size = f_out.tell() - cd_offset

        # End of Central Directory Record
        f_out.write(b'PK\x05\x06')
        f_out.write(struct.pack('<HHHHIIH', 0, 0, len(cd_entries), len(cd_entries), cd_size, cd_offset, 0))

    print(f"Aligned APK written to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: zipalign.py <input.apk> <output.apk>")
        sys.exit(1)
    align_apk(sys.argv[1], sys.argv[2])
