import numpy as np
from sklearn.cluster import DBSCAN, KMeans

AVG_EARTH_RADIUS = 6371


def _haversine_array(lat1, lng1, lat2, lng2):
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = np.sin(lat * 0.5) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * np.arcsin(np.sqrt(d))

    return h


def dummy_manhattan_distance(row):
    lat1, lng1, lat2, lng2 = map(np.radians, row)
    a = _haversine_array(lat1, lng1, lat1, lng2)
    b = _haversine_array(lat1, lng1, lat2, lng2)
    return a + b


def bearing_array(row):
    lat1, lng1, lat2, lng2 = row
    lng_delta_rad = np.radians(lng2 - lng1)
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    y = np.sin(lng_delta_rad) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(lng_delta_rad)
    return np.degrees(np.arctan2(y, x))


def center_lat_feat(row):
    lat1, lng1, lat2, lng2 = row
    center_lat = (lat1 + lat2) / 2

    return center_lat


def center_lng_feat(row):
    lat1, lng1, lat2, lng2 = row
    center_lng = (lng1 + lng2) / 2

    return center_lng


def coords_clusters_dbscan(coords):

    coords_flat = np.vstack((coords[['sourceLatitude', 'sourceLongitude']].values,
                             coords[['destinationLatitude', 'destinationLongitude']].values))

    clusters = DBSCAN(eps=0.01, min_samples=5, leaf_size=30).fit_predict(coords_flat)
    src_cluster = clusters[:len(coords)]
    dest_cluster = clusters[len(coords):]

    return src_cluster, dest_cluster


def coords_clusters_kmeans(coords, n_clusters):

    coords_flat = np.vstack((coords[['sourceLatitude', 'sourceLongitude']].values,
                             coords[['destinationLatitude', 'destinationLongitude']].values))

    model = KMeans(n_clusters=n_clusters, random_state=42).fit(coords_flat)
    src_cluster = model.predict(coords[['sourceLatitude', 'sourceLongitude']])
    dest_cluster = model.predict(coords[['destinationLatitude', 'destinationLongitude']])

    return src_cluster, dest_cluster


def coord_features(data, features, do_clusters=True):
    coords = data[['sourceLatitude', 'sourceLongitude', 'destinationLatitude', 'destinationLongitude']]
    features['dmd'] = coords.apply(dummy_manhattan_distance, axis=1)
    features['bearing_array'] = coords.apply(bearing_array, axis=1)
    features['center_lat'] = coords.apply(center_lat_feat, axis=1)
    features['center_lng'] = coords.apply(center_lng_feat, axis=1)

    if do_clusters:
        features['cluster_src_db'], features['cluster_dest_db'] = coords_clusters_dbscan(coords)
        features['cluster_src_km'], features['cluster_dest_km'] = coords_clusters_kmeans(coords, n_clusters=120)

    return features