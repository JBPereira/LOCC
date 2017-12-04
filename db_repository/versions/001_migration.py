from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
data = Table('data', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
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
    post_meta.tables['data'].columns['datetime'].create()
    post_meta.tables['data'].columns['humidity'].create()
    post_meta.tables['data'].columns['latitude'].create()
    post_meta.tables['data'].columns['sun_intensity'].create()
    post_meta.tables['data'].columns['temperature'].create()
    post_meta.tables['data'].columns['temperature_10cm'].create()
    post_meta.tables['data'].columns['tide'].create()
    post_meta.tables['data'].columns['visibility_meters'].create()
    post_meta.tables['data'].columns['water_drainage'].create()
    post_meta.tables['data'].columns['water_flow'].create()
    post_meta.tables['data'].columns['water_level'].create()
    post_meta.tables['data'].columns['water_level_belgium_border'].create()
    post_meta.tables['data'].columns['waves_height'].create()
    post_meta.tables['data'].columns['wind_blast'].create()
    post_meta.tables['data'].columns['wind_direction'].create()
    post_meta.tables['data'].columns['wind_direction_degrees'].create()
    post_meta.tables['data'].columns['wind_speedBF'].create()
    post_meta.tables['data'].columns['wind_speedMS'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['data'].columns['datetime'].drop()
    post_meta.tables['data'].columns['humidity'].drop()
    post_meta.tables['data'].columns['latitude'].drop()
    post_meta.tables['data'].columns['sun_intensity'].drop()
    post_meta.tables['data'].columns['temperature'].drop()
    post_meta.tables['data'].columns['temperature_10cm'].drop()
    post_meta.tables['data'].columns['tide'].drop()
    post_meta.tables['data'].columns['visibility_meters'].drop()
    post_meta.tables['data'].columns['water_drainage'].drop()
    post_meta.tables['data'].columns['water_flow'].drop()
    post_meta.tables['data'].columns['water_level'].drop()
    post_meta.tables['data'].columns['water_level_belgium_border'].drop()
    post_meta.tables['data'].columns['waves_height'].drop()
    post_meta.tables['data'].columns['wind_blast'].drop()
    post_meta.tables['data'].columns['wind_direction'].drop()
    post_meta.tables['data'].columns['wind_direction_degrees'].drop()
    post_meta.tables['data'].columns['wind_speedBF'].drop()
    post_meta.tables['data'].columns['wind_speedMS'].drop()
