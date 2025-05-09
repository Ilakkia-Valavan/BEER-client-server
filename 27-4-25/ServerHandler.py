import ast
import socket
import threading
import json
import random
import signal
import sys
import time
from ServerMessageUtil import ServerMessageUtil
from battleship import Board, parse_coordinate, SHIPS
from Utility import Util

class ServerHandler:

    client_detail = {}

    def handle(self, message):
        print("")

    