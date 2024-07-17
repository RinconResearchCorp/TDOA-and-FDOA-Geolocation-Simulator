import numpy as np

c = 2.99792458e8
f0 = 1090e6

def const_fdoa(
        X: np.ndarray, 
        V: np.ndarray, 
        X1: np.ndarray, 
        X2: np.ndarray) -> float:
    """
    Gives the equation for line of constant FDOA between two receivers and an emitter
    
    params:
        X: Position of the emitter
        V: Velocity of the emitter
        X1: Position of the first receiver
        X2: Position of the second receiver
    returns:
        The value of the equation at the given point
    """
    vel1 = np.dot(V, (X - X1))
    vel2 = np.dot(V, (X - X2))
    dist1 = np.linalg.norm(X- X1)
    dist2 = np.linalg.norm(X- X2)
    return (vel1 / dist1 - vel2 / dist2)

def const_fdoa_grad(
        X: np.ndarray, 
        V: np.ndarray, 
        X1: np.ndarray, 
        X2: np.ndarray) -> np.ndarray:
    x = X[0]
    y = X[1]
    vx = V[0]
    vy = V[1]
    x1 = X1[0]
    y1 = X1[1]
    x2 = X2[0]
    y2 = X2[1]
    dist1 = np.linalg.norm(X- X1)
    dist2 = np.linalg.norm(X- X2)
    vel1 = np.dot(V, (X - X1))
    vel2 = np.dot(V, (X - X2))
    return np.array([vx/dist1 - (vel1 * (x-x1) / dist1**3) - vx / dist2 + (vel2 * (x-x2) / dist2**3),
                     vy/dist1 - (vel1 * (y-y1) / dist1**3) - vy / dist2 + (vel2 * (y-y2) / dist2**3),
                     (x-x1)/dist1 - (x-x2)/dist2,
                     (y-y1)/dist1 - (y-y2)/dist2])

def const_tdoa(
        X: np.ndarray, 
        X1: np.ndarray, 
        X2: np.ndarray) -> float:
    """
    Gives the equation for line of constant TDOA between two receivers and an emitter
    
    params:
        X: Position of the emitter
        X1: Position of the first receiver
        X2: Position of the second receiver
        t1: TDOA at the first receiver
        t2: TDOA at the second receiver
    returns:
        The value of the equation at the given point
    """
    dist1 = np.linalg.norm(X- X1)
    dist2 = np.linalg.norm(X- X2)
    return dist1 - dist2 

def const_tdoa_grad(
        X: np.ndarray, 
        X1: np.ndarray, 
        X2: np.ndarray) -> np.ndarray:
    x = X[0]
    y = X[1]
    x1 = X1[0]
    y1 = X1[1]
    x2 = X2[0]
    y2 = X2[1]
    dist1 = np.linalg.norm(X- X1)
    dist2 = np.linalg.norm(X- X2)
    return np.array([(x-x1)/dist1 - (x-x2)/dist2,
                     (y-y1)/dist1 - (y-y2)/dist2,
                     0,
                     0])

def jacobian(X, V, X1, X2, X3):
    return np.array([const_fdoa_grad(X, V, X1, X2),
                     const_fdoa_grad(X, V, X1, X3),
                     const_tdoa_grad(X, X1, X2),
                     const_tdoa_grad(X, X1, X3)])

def main():
    emitter_pos = np.array([100, 400])
    emitter_vel = np.array([150, 200])

    receiver1_pos = np.array([0,0])
    receiver2_pos = np.array([0,1000])
    receiver3_pos = np.array([250,750])

    t1 = np.linalg.norm(emitter_pos - receiver1_pos) 
    t2 = np.linalg.norm(emitter_pos - receiver2_pos) 
    t3 = np.linalg.norm(emitter_pos - receiver3_pos) 
    t12 = t1 - t2
    t13 = t1 - t3

    f1 = np.dot(emitter_vel, receiver1_pos - emitter_pos) / np.linalg.norm(emitter_pos - receiver1_pos)
    f2 = np.dot(emitter_vel, receiver2_pos - emitter_pos) / np.linalg.norm(emitter_pos - receiver2_pos) 
    f3 = np.dot(emitter_vel, receiver3_pos - emitter_pos) / np.linalg.norm(emitter_pos - receiver3_pos)
    f12 = f1 - f2
    f13 = f1 - f3

    cov = np.eye(4)
    # Fill diagonal with true expected errors
    cov[0,0] = 1527 # std dev in freq
    cov[1,1] = 1527
    cov[2,2] = .006 # std dev in time
    cov[3,3] = .006 

    jac = jacobian(emitter_pos, emitter_vel, receiver1_pos, receiver2_pos, receiver3_pos)
    jacT = jac.T

    err = jac @ cov @ jacT

    print(err)

if __name__ == "__main__":
    main()