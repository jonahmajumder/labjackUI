import u3
from time import sleep

d = u3.U3()

d.getFeedback(u3.BitDirWrite(4, 1))

def set_state(state):
	if state:
		d.getFeedback(u3.BitStateWrite(4, 0))
	else:
		d.getFeedback(u3.BitStateWrite(4, 1))


while True:
	set_state(True)
	sleep(0.25)
	set_state(False)
	sleep(0.25)