"""
Helper program to build VOD file
"""

import logging
import asyncio
import binascii
import os

from MerkleHashTree import MerkleHashTree
from GlobalParams import GlobalParams
from MemoryChunkStorage import MemoryChunkStorage
from ContentGenerator import ContentGenerator


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s %(message)s')

class FakeSwarm(object):
    """Fake Swarm object to be inserted instead of real swarm"""
    
    def __init__(self):
        """Build required parameters"""
        self.discard_wnd = None
        self.set_have = set()
        self.live = True
        self.live_src = True
        self._have_ranges = []
        self._last_discarded_id = 0

    def SendHaveToMembers(self):
        """Do nothing"""
        pass

def main(length, filename):
    """Generate file having length number of seconds and save to filename"""

    logging.info('Building VOD file. Length: %s s. Filename: %s', length, filename)

    swarm = FakeSwarm()
    storage = MemoryChunkStorage(swarm)
    generator = ContentGenerator()

    fps = 10
    key = 0
    total_frames = length * fps
    for _ in range(total_frames):
        # Generate AV data
        if key == min([
            len(generator._audio_samples),
            len(generator._video_samples)
        ]):
            key = 0

        avdata = generator._get_next_avdata(key)
        key += 1

        # Feed it into storage
        storage.pack_data_with_de(avdata)

    storage_len = len(storage._chunks)
    logging.info('Total frames: %s Total chunks: %s',
                 total_frames,
                 storage_len
    )

    # Storage now has all data. Store it into file
    with open(filename, 'wb') as file_hdl:
        for key, val in storage._chunks.items():
            file_hdl.write(val)
            if key % 1000 == 0:
                logging.info('Wrote chunk %s of %s', key, storage_len)


    # Calculate Merkle Root Hash:
    logging.info('Calculating Merkle root hash')
    mekle_hasher = MerkleHashTree('sha1', GlobalParams.chunk_size)
    mrh = mekle_hasher.get_file_hash(filename)

    logging.info('Merkle Root hash: %s',
                 binascii.hexlify(mrh)
    )

    with open('{}.log'.format(filename), 'a') as log_hdl:
        log_hdl.write('Filename: {}'.format(filename) + os.linesep)
        log_hdl.write('Total frames: {}'.format(total_frames) + os.linesep)
        log_hdl.write('Total chunks: {}'.format(storage_len) + os.linesep)
        log_hdl.write('Merkle hash: {}'.format(binascii.hexlify(mrh)) + os.linesep)

if __name__ == '__main__':
    main(333, 'vod333.dat')