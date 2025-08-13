# node.py
from abc import abstractmethod
import lcm
import threading

class Node:
    def __init__(self):
        self.running = False

    def subscribe(self, channel, handler):
        self.lc.subscribe(channel, handler)

    def publish(self, channel, msg):
        self.lc.publish(channel, msg.encode())

    def _handle_loop(self):
        while self.running:
            self.lc.handle_timeout(10)  # 10ms timeout to check for messages

    def stop(self):
        self.running = False
        
        if self.thread.is_alive():
            try:
                self.thread.join()
            except Exception as e:
                print(f"Error joining thread: {e}")
            
        self.on_stop()
    
    def launch_node(self):
        self.lc = lcm.LCM()
        self.running = True
        self.on_start()
        
        # Start the LCM handling loop in a background thread.
        self.thread = threading.Thread(target=self._handle_loop, daemon=True)
        self.thread.start()
        
        self.run()
        self.stop()
                
    @abstractmethod 
    def on_start(self):
        """
            This method is called once when the node is launched. Put all the initialization code here.
        """
        pass
    
    @abstractmethod 
    def run(self):
        """
            Main code for node. Once this function finishes, the node terminates.
        """
        pass
    
    @abstractmethod
    def on_stop(self):
        """
            This method is called once when the node is terminated. Put all the cleanup code here.
        """
        pass