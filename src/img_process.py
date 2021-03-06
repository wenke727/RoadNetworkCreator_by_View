import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from PIL import Image

import math

from db.db_process import load_from_DB
from utils.geo_plot_helper import map_visualize
from utils.spatialAnalysis import linestring_length
from utils.utils import load_config

""" import road network from OSM """
import pickle
from road_network import OSM_road_network


DB_pano_base, DB_panos, DB_connectors, DB_roads = load_from_DB(False)

config = load_config()
pano_dir = config['data']['pano_dir']
pano_group_dir = config['data']['pano_group_dir']
DF_matching = pd.read_csv( config['data']['df_matching'])


linestring_length(DB_roads, True)

osm_shenzhen = pickle.load(open("../input/road_network_osm_shenzhen.pkl", 'rb') )
df_nodes = osm_shenzhen.nodes
df_edges = osm_shenzhen.edges
df_edges.reset_index(drop=True, inplace=True)
df_edges.loc[:,'rid'] = df_edges.loc[:,'rid'].astype(np.int)




def get_pano_id_by_rid(rid):
    return DB_panos.query( f"RID=='{rid}' " )


def fig2data(fig):
    """
    fig = plt.figure()
    image = fig2data(fig)
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    import PIL.Image as Image
    # draw the renderer
    fig.canvas.draw()
 
    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    image = Image.frombytes("RGBA", (w, h), buf.tostring())
    image = np.asarray(image)
    return image


def plot_pano_and_its_view(pid, heading=None):
    """绘制pano所在的路段，位置以及视角

    Args:
        pid ([type]): [description]
    """
    rid = DB_panos.query( f"PID=='{pid}' " ).RID.iloc[0]
    pid_record = get_pano_id_by_rid(rid).query( f"PID == '{pid}'" )
    assert( len(pid_record) > 0 )
    pid_record = pid_record.iloc[0]

    if heading is None:
        heading = pid_record.DIR
    x, y = pid_record.geometry.coords[0]
    
    fig, ax = map_visualize( DB_roads.query( f"RID == '{pid_record.RID}' " ), label="Lane" )

    x0, x1 = ax.get_xlim()
    aus_line_len = (x1-x0)/20
    dy, dx = math.cos(heading/180*math.pi) * aus_line_len, math.sin(heading/180*math.pi) * aus_line_len
    ax.annotate('', xy=(x+dx, y+dy), xytext= (x,y) ,arrowprops=dict(facecolor='blue', shrink=0.05, alpha=0.5))
    gpd.GeoSeries( [Point(x, y)] ).plot(ax=ax, label='Pano' )

    plt.axis('off')
    plt.legend()
    plt.tight_layout()
    return fig

# 在街景中添加位置示意图

pid = '09005700121709091541462499Y'
position = plot_pano_and_its_view( pid = '09005700121709091541462499Y' )
position.savefig('./test.jpg', pad_inches=0, bbox_inches='tight')
position = Image.open('./test.jpg')


img = Image.open('/home/pcl/Data/minio_server/panos/989d83-aa81-9df2-b360-685876_02_09005700121709091541462499Y_269.jpg')
# 将一张图粘贴到另一张图像上
x, y = [ int(x/3) for x in img.size]
x = int(position.size[1] *y/position.size[0])

location_illustration = position.resize((x, y))
img.paste( location_illustration, [0,0,x,y] )
img


plt.imshow(img)










