from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
DataTable = Table('DataTable', pre_meta,
    Column('index', BIGINT),
    Column('latitude', TEXT),
    Column('wind_speedBF', TEXT),
    Column('wind_speedMS', TEXT),
    Column('humidity', TEXT),
    Column('wind_direction', TEXT),
    Column('longitude', TEXT),
    Column('temperature', TEXT),
    Column('wind_direction_degrees', TEXT),
    Column('visibility_meters', TEXT),
    Column('sun_intensity', TEXT),
    Column('temperature_10cm', TEXT),
    Column('wind_blast', TEXT),
    Column('water_level', FLOAT),
    Column('datetime', TEXT),
    Column('water_flow', FLOAT),
    Column('waves_height', FLOAT),
    Column('water_level_belgium_border', FLOAT),
    Column('tide', FLOAT),
    Column('water_drainage', FLOAT),
)

data = Table('data', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('index', Integer),
    Column('longitude', Integer),
    Column('wind_direction', Integer),
    Column('latitude', Integer),
    Column('humidity', Integer),
    Column('temperature_10cm', Integer),
    Column('wind_direction_degrees', Integer),
    Column('temperature', Integer),
    Column('wind_blast', Integer),
    Column('wind_speedMS', Integer),
    Column('visibility_meters', Integer),
    Column('wind_speedBF', Integer),
    Column('sun_intensity', Integer),
    Column('datetime', Integer),
    Column('water_flow', Integer),
    Column('waves_height', Integer),
    Column('water_drainage', Integer),
    Column('water_level', Integer),
    Column('water_level_belgium_border', Integer),
    Column('tide', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['DataTable'].drop()
    post_meta.tables['data'].columns['index'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['DataTable'].create()
    post_meta.tables['data'].columns['index'].drop()
