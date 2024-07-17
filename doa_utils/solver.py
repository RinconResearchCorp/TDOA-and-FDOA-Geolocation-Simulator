from typing import Optional, List
import warnings
import numpy as np
from scipy.optimize import least_squares
from .signal_generator import Receiver

c = 2.99792458e8
f0 = 1090e6

def estimate_emitter(
        receivers:  List[Receiver],
        fdoa_data: Optional[List[float]] = None,
        toa_data: Optional[List[float]] = None,
        emitter_velocity: Optional[np.ndarray] = None,
                   ) -> np.ndarray:
    """
    Given a list of receivers and some set of measured data, selects the 
    best solver if possible, and returns the estimated emitter position. 
    
    params:
        receivers: List of Receiver objects initialized with position information
        fdoa_data: List of FDOA measurements
        toa_data: List of TDOA measurements
        emitter_velocity: Velocity of the emitter
    returns:
        Estimated emitter position
    
    """
    receiver_X_list = [receiver.position for receiver in receivers]
    
    # let initial guess be centroid I guess? Until we have a more sophisticated search algo.
    x0 = np.sum(receiver_X_list, axis=0) / len(receiver_X_list)
    if fdoa_data and toa_data:
        v0 = np.zeros(x0.shape)
        x0 = np.concatenate((x0, v0))
        obj = lambda Z : fdoa_with_tdoa(Z, receiver_X_list, fdoa_data, toa_data)
    elif fdoa_data is not None and emitter_velocity is not None:
        obj = lambda X : fdoa_v_known(X, emitter_velocity, receiver_X_list, fdoa_data)
    elif toa_data:
        obj = lambda X : tdoa(X, receiver_X_list, toa_data)
    elif fdoa_data:
        v0 = np.zeros(x0.shape)
        x0 = np.concatenate((x0, v0))
        obj = lambda Z : fdoa_v_unknown(Z, receiver_X_list, fdoa_data)
    else:
        raise ValueError("Need at least one type of data to solve for emitter position")

    solution = least_squares(obj, x0)
    if solution.success:
        return solution.x
    else:
        warnings.warn("Solver failed to converge")
        return solution.x
    

def const_fdoa(
        X: np.ndarray, 
        V: np.ndarray, 
        X1: np.ndarray, 
        X2: np.ndarray, 
        f1: float, 
        f2: float) -> float:
    """
    Gives the equation for line of constant FDOA between two receivers and an emitter
    
    params:
        X: Position of the emitter
        V: Velocity of the emitter
        X1: Position of the first receiver
        X2: Position of the second receiver
        f1: FDOA at the first receiver
        f2: FDOA at the second receiver
    returns:
        The value of the equation at the given point
    """
    vel1 = np.dot(V, (X - X1))
    vel2 = np.dot(V, (X - X2))
    dist1 = np.linalg.norm(X- X1)
    dist2 = np.linalg.norm(X- X2)
    return (vel1 / dist1 - vel2 / dist2 - c / f0 * (f1 - f2))

def const_tdoa(
        X: np.ndarray, 
        X1: np.ndarray, 
        X2: np.ndarray, 
        t1: float, 
        t2: float) -> float:
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
    return dist1 - dist2 - (t1 - t2) * c

def fdoa_v_known(
        X: np.ndarray, 
        V: np.ndarray, 
        receiver_X_list: List[np.ndarray], 
        fdoa_list: List[float]) -> List[float]:
    """
    Objective function for least squares optimization of emitter position
    when emitter velocity is known or being approximated.
    
    params:
        X: Position of the emitter
        V: Velocity of the emitter
        receiver_X_list: List of receiver positions
        fdoa_list: List of FDOA measurements
    returns:
        The value of the objective function at the given point
    """
    dims = X.shape[0]
    if dims == 2 and len(receiver_X_list) < 3:
        raise ValueError("Need at least 3 receivers for 2D")
    if dims == 3 and len(receiver_X_list) < 4:
        raise ValueError("Need at least 4 receivers for 3D")
    
    assert len(receiver_X_list) == len(fdoa_list)

    ref = receiver_X_list[0]
    f1 = fdoa_list[0]
    return [const_fdoa(X, V, ref, receiver_X_list[i], f1, fdoa_list[i]) for i in range(1, len(receiver_X_list))]

def fdoa_v_unknown(
        Z: np.ndarray, 
        receiver_X_list: List[np.ndarray], 
        fdoa_list: List[float]) -> List[float]:
    """
    Objective function for least squares optimization of emitter position
    and velocity when emitter velocity is unknown.

    params:
        Z: Concatenation of emitter position and velocity
        receiver_X_list: List of receiver positions
        fdoa_list: List of FDOA measurements
    returns:
        The value of the objective function at the given point
    """
    mid = Z.shape[0] // 2
    X = Z[:mid]
    V = Z[mid:]
    dims = X.shape[0]
    if dims == 2 and len(receiver_X_list) < 5:
        raise ValueError("Need at least 5 receivers for 2D")
    if dims == 3 and len(receiver_X_list) < 7:
        raise ValueError("Need at least 7 receivers for 3D")
    
    assert len(receiver_X_list) == len(fdoa_list)

    ref = receiver_X_list[0]
    f1 = fdoa_list[0]
    return [const_fdoa(X, V, ref, receiver_X_list[i], f1, fdoa_list[i]) for i in range(1, len(receiver_X_list))]

def fdoa_with_tdoa(
        Z: np.ndarray, 
        receiver_X_list: List[np.ndarray], 
        fdoa_list: List[float], 
        toa_list: List[float]) -> List[float]:
    """
    Objective function for least squares optimization of emitter position
    and velocity when emitter velocity is unknown but TDOA data is present

    params:
        Z: Concatenation of emitter position and velocity
        receiver_X_list: List of receiver positions
        fdoa_list: List of FDOA measurements
        toa_list: List of relative TOA measurements, i.e. if toa_list = np.array([0, 10])
            then the second receiver received the signal 10 seconds after the first
    """
    mid = Z.shape[0] // 2
    X = Z[:mid]
    V = Z[mid:]
    dims = X.shape[0]
    
    if dims == 2 and len(receiver_X_list) < 3:
        raise ValueError("Need at least 3 receivers for 2D")
    if dims == 3 and len(receiver_X_list) < 4:
        raise ValueError("Need at least 4 receivers for 3D")
    
    assert len(receiver_X_list) == len(fdoa_list) == len(toa_list)

    ref = receiver_X_list[0]
    f1 = fdoa_list[0]
    t1 = toa_list[0]
    
    fdoa_eqns = [const_fdoa(X, V, ref, receiver_X_list[i], f1, fdoa_list[i]) for i in range(1, len(receiver_X_list))]
    tdoa_eqns = [const_tdoa(X, ref, receiver_X_list[i], t1, toa_list[i]) for i in range(1, len(receiver_X_list))]
    return fdoa_eqns + tdoa_eqns

def tdoa(
        X: np.ndarray, 
        receiver_X_list: List[np.ndarray], 
        toa_list: List[float]) -> List[float]:
    """
    Objective function for least squares optimization of emitter position
    when only using TDOA data.

    params:
        X: Position of the emitter
        receiver_X_list: List of receiver positions
        toa_list: List of relative TOA measurements, i.e. if toa_list = np.array([0, 10])
            then the second receiver received the signal 10 seconds after the first
    returns:
        The value of the objective function at the given point
    """
    dims = X.shape[0]
    if dims == 2 and len(receiver_X_list) < 3:
        raise ValueError("Need at least 3 receivers for 2D")
    if dims == 3 and len(receiver_X_list) < 4:
        raise ValueError("Need at least 4 receivers for 3D")
    
    assert len(receiver_X_list) == len(toa_list)

    ref = receiver_X_list[0]
    t1 = toa_list[0]

    return [const_tdoa(X, ref, receiver_X_list[i], t1, toa_list[i]) for i in range(1, len(receiver_X_list))]

