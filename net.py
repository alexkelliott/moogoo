HEADERSIZE = 10

def send_data(sock, msg):
	msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
	sock.send(msg)

	
def rec_data(sock):
	full_msg = b''
	new_msg = True
	while True:
		msg = sock.recv(16)

		if new_msg:
			msglen = int(msg[:HEADERSIZE])
			new_msg = False

		full_msg += msg

		if len(full_msg)-HEADERSIZE == msglen:
			break

	return full_msg[HEADERSIZE:]