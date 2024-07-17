import pymap3d as pm

def main():
    receiver_X_list = [
    [40.7128, -74.0060, 10],
    [41.7128, -74.0060, 15],
    [42.7128, -74.0060, 20]
    ]
    receiver_cartesian = []
    receiver_geo = []
    lat0, lon0, alt0 = receiver_X_list[0]
    for X in receiver_X_list:
        e, n, u = pm.geodetic2enu(X[0], X[1], X[2], lat0, lon0, alt0)
        curr_pos = [e, n, u]
        receiver_cartesian.append(curr_pos)
    print(receiver_cartesian)

    for X in receiver_cartesian:
        lat, lon, alt = pm.enu2geodetic(X[0], X[1], X[2], lat0, lon0, alt0)
        curr_pos = [lat, lon, alt]
        receiver_geo.append(curr_pos)
    print(receiver_geo)

if __name__ == "__main__":
    main()