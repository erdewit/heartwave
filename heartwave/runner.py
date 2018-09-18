import asyncio
import threading
import queue


class Runner:
    """
    General processing stage that can be fed input, run some processing
    in a separate thread and make the results available by awaiting
    or as an asynchronous iterator.
    """
    Stop = object()

    def __init__(self):
        self.inQ = queue.Queue()
        self.outQ = asyncio.Queue()
        self.running = False
        self._thread = None
        self._loop = asyncio.get_event_loop()

    def __len__(self):
        return self.outQ.qsize()

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, *_excinfo):
        self.stop()

    async def __aiter__(self):
        if not self.running:
            self.start()
        return self

    async def __anext__(self):
        if self.running:
            result = await self.outQ.get()
            if result is not Runner.Stop:
                return result
        raise StopAsyncIteration

    def __await__(self):
        return (yield from self.outQ.get())

    def __iter__(self):
        return self

    def __next__(self):
        if self.outQ.qsize():
            return self.outQ.get_nowait()
        else:
            raise StopIteration

    def start(self):
        """
        Start processing.
        """
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def stop(self):
        """
        Stop processing.
        """
        if not self.running:
            return
        self.running = False
        self.inQ.put_nowait(Runner.Stop)
        self.outQ.put_nowait(Runner.Stop)
        self._thread.join()
        self._thread = None
        self.outQ = asyncio.Queue()

    def feed(self, data):
        """
        Feed input to be processed.
        """
        self.inQ.put_nowait(data)
        return self

    __iadd__ = feed

    def output(self, result):
        """
        Add result of processing to the output of this iterator.
        """
        self._loop.call_soon_threadsafe(self.outQ.put_nowait, result)

    def hasOutput(self):
        """
        Is there any output ready?
        """
        return self.outQ.qsize() > 0

    def getInput(self):
        """
        Get next input element.
        """
        return self.inQ.get()

    def getLatestInput(self):
        """
        Get latest input element, skipping over earlier input.
        """
        data = self.inQ.get()
        try:
            while True:
                data = self.inQ.get_nowait()
        except queue.Empty:
            pass
        return data

    def run(self):
        """
        Processing loop. Implementations should stop when self.running
        is False or when Pipeline.Stop is encountered in the input queue.
        """
        pass
