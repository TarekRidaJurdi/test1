from PIL import Image
import PIL
import qrcode
pathes=[
'1bsNSOd2se59GdYbrZqT9xEo-WC9wIPCk',
'188VuNWGTL7uNqrNy-ScRsXWRMF7Xo8oy',
'1sffEwmm9ICweNcQ50fuE3M8vIdUsF8py',
'1vf8ozCEmOgi2YBD2E7aDL7COdDuCc41v',
'1XDlRTFqM7MmhH9dIaOrA_cerHeIQbAyc',
'1N_UIkd_3zdEAAfw7wtKv3VEV4ieVqiyj',
'1NPSsn4wdRkxuKBx71Xv6veCrS5EYac19'

]
for x in range(len(pathes)):
    qr = qrcode.QRCode()
    qr.add_data(pathes[x])
    qr.make()
    img = qr.make_image()
    im1 = img.save(r"C:\Users\S.C.C\Desktop\Roaea_project\QR\{}.png".format(x))
    