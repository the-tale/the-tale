

def chunks(sequence, chunk_size):
    for i in range(0, len(sequence), chunk_size):
        yield sequence[i:i + chunk_size]
