# coding:utf-8
# !/usr/bin/env python
import sys
from math import sqrt, sin, cos, atan2

__author__ = 'wanglei'


reload(sys)
sys.setdefaultencoding('utf8')

pi = 3.14159265358979324
a = 6378245.0
ee = 0.00669342162296594323
x_pi = 3.14159265358979324 * 3000.0 / 180.0


class TransformationLocation(object):
    """ 坐标转换：地球坐标转换为火星坐标

    """

    @staticmethod
    def out_of_china(lat, lon):

        if lon < 72.004 or lon > 137.8347:
            return True
        if lat < 0.8293 or lat > 55.8271:
            return True
        return False

    @staticmethod
    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * sqrt(abs(x))
        ret += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0
        ret += (20.0 * sin(y * pi) + 40.0 * sin(y / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * sin(y / 12.0 * pi) + 320 * sin(y * pi / 30.0)) * 2.0 / 3.0
        return ret

    @staticmethod
    def transform_lon(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * sqrt(abs(x))
        ret += (20.0 * sin(6.0 * x * pi) + 20.0 * sin(2.0 * x * pi)) * 2.0 / 3.0
        ret += (20.0 * sin(x * pi) + 40.0 * sin(x / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * sin(x / 12.0 * pi) + 300.0 * sin(x / 30.0 * pi)) * 2.0 / 3.0
        return ret

    def transform_mars(self, wg_lat, wg_lon):
        """ 地球坐标转换为火星坐标

        :param wg_lat:
        :type wg_lat:
        :param wg_lon:
        :type wg_lon:
        :return:
        :rtype:
        """
        if self.out_of_china(wg_lat, wg_lon):
            return wg_lon, wg_lat

        d_lat = self.transform_lat(wg_lon - 105.0, wg_lat - 35.0)
        d_lon = self.transform_lon(wg_lon - 105.0, wg_lat - 35.0)
        rad_lat = wg_lat / 180.0 * pi
        magic = sin(rad_lat)
        magic = 1 - ee * magic * magic
        sqrt_magic = sqrt(magic)
        d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * pi)
        d_lon = (d_lon * 180.0) / (a / sqrt_magic * cos(rad_lat) * pi)
        mg_lat = wg_lat + d_lat
        mg_lon = wg_lon + d_lon

        return mg_lon, mg_lat

    @staticmethod
    def bd_encrypt(gg_lat, gg_lon):
        """ 火星坐标转百度坐标

        :param gg_lat:
        :type gg_lat:
        :param gg_lon:
        :type gg_lon:
        :return:
        :rtype:
        """
        x = gg_lon
        y = gg_lat
        z = sqrt(x * x + y * y) + 0.00002 * sin(y * x_pi)
        theta = atan2(y, x) + 0.000003 * cos(x * x_pi)
        bd_lon = z * cos(theta) + 0.0065
        bd_lat = z * sin(theta) + 0.006

        return bd_lon, bd_lat

    @staticmethod
    def bd_decrypt(bd_lat, bd_lon):
        """ 百度坐标转火星坐标

        :param bd_lat:
        :type bd_lat:
        :param bd_lon:
        :type bd_lon:
        :return:
        :rtype:
        """
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = sqrt(x * x + y * y) - 0.00002 * sin(y * x_pi)
        theta = atan2(y, x) - 0.000003 * cos(x * x_pi)
        gg_lon = z * cos(theta)
        gg_lat = z * sin(theta)

        return gg_lon, gg_lat


# if __name__ == '__main__':
#
#     # aa = TransformationLocation()
#     # gg_lon, gg_lat = aa.transform_mars(39.967224, 116.410042)
#     # lon, lat = aa.bd_encrypt(gg_lat, gg_lon)
#     # geo_point_a = GeoPoint(87.624176, 43.809495)
#     # geo_point_b = GeoPoint(39.975006, 116.42263)
#     #
#     # point_distance = geo_point_a.distance_to(geo_point_b)
#     # print lon, lat
#     # print point_distance * 1000
#     ip_address = '123.151.12.154'
#     city_file = os.path.join(Settings.SITE_ROOT_PATH, u"app/handlers/GeoLiteCity.dat")
#     geo_ip = pygeoip.GeoIP(city_file, pygeoip.MEMORY_CACHE)
#     location = geo_ip.record_by_addr(ip_address)
#     if location is not None:
#         latitude = location['latitude']
#         longitude = location['longitude']
#         print latitude, longitude
#
#     geo_hashcode = geohash.encode(43.830309, 87.605779, 6)
#     print geo_hashcode


