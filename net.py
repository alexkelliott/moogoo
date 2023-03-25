HEADERSIZE: int = 10

def send_data(sock, msg) -> None:
	msg: bytes = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
	sock.send(msg)

	
def rec_data(sock) -> bytes:
	full_msg: bytes = b''
	new_msg: bool = True

	while True:
		msg: bytes = sock.recv(16)

		if new_msg:
			msglen: int = int(msg[:HEADERSIZE])
			new_msg = False

		full_msg += msg

		if len(full_msg)-HEADERSIZE == msglen:
			break

	return full_msg[HEADERSIZE:]