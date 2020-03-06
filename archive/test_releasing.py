from u3 import U3
import weakref

u = U3()

r = weakref.ref(u, lambda ref: print('Deleting {}.'.format(ref)))

del u

print('Last line of program.')