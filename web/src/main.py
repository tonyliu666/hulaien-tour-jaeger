
from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
# from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
# from opentelemetry.instrumentation.flask import FlaskInstrumentor
# from tracing import init_tracer
########## opentelemetry
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor,ConsoleSpanExporter

from opentelemetry.sdk.resources import Resource

import logging
import os,sys
import re 
from Crawler import crawl
from Crawler import selenium,store,fig_store,click_store
from send_email import SendEmail,Value
# opentracing get the current span and traceIDs
# import opentracing
# tracer = init_tracer('flask')

from opentelemetry.instrumentation.logging import LoggingInstrumentor
LoggingInstrumentor().instrument(set_logging_format=True,loggin_format='%(otelSpanID)s %(otelTraceID)s %(otelServiceName)s %(otelTraceSampled)s')


## -------------jaeger exporter-------------------
resource = Resource.create({"service.name": "flask-app"})
provider = TracerProvider(resource=resource)
jaeger_exporter = JaegerExporter(
    # service_name="flask-app",
    agent_host_name='Jaeger',
    agent_port=6831,
    username="tony"
    # collector_endpoint=14268
)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

## -------------logging appender and consoleexporter-------------- 
logger = logging.getLogger(__name__)
logging_resource = Resource.create({"service.name": "logging_service"})
logging_provider = TracerProvider(resource=logging_resource)
logging_processor = BatchSpanProcessor(ConsoleSpanExporter())
logging_provider.add_span_processor(logging_processor)
trace.set_tracer_provider(logging_provider)

# -------------python flask app----------------
app = Flask(__name__, template_folder='templates')
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
host = os.environ.get('POSTGRES_HOST') 
port = os.environ.get('POSTGRES_PORT')
database = os.environ.get('POSTGRES_DB') 

# conn_string = f"dbname='{database}'user='{user}'host='{host}'port='{port}'"

# conn = psycopg2.connect(
#     conn_string
# )
# cur = conn.cursor()
def connect_db():
    # with tracer.start_active_span('db') as scope:
        DATABASE_CONNECTION_URI = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        # scope.span.log_kv({'event':'setting'})
        return db 
# DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
db = connect_db()
#-------------------------------------------------------
class Todo(db.Model): 
    __tablename__ = 'image'
    # _id = db.Column("id",db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), unique=True, nullable=False)
    imglink = db.Column(db.String(100),nullable=False)
    loc =  db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.id
    def __init__ (self,link,title,imglink,loc):
        self.link = link
        self.title = title
        self.imglink = imglink
        self.loc = loc   
# cur = conn.cursor() 
def GetTraceSpanID(span):
    trace_id=""
    span_id=""
    if span is not None:
        attribute = list(span.context.__repr__().split(" "))
        trace_id = attribute[0][21:]
        span_id = attribute[1][8:]
    return trace_id,span_id
@app.route('/')
def index(): 
    # with tracer.start_active_span('home') as scope:
        # scope.span.log_kv({'message': 'this is the home page'})
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)
        logger.info('GET: 200 / '+'traceid: '+trace_id+' spanid: '+span_id)
        return render_template('home.html')
@app.route('/Taipei',methods=["GET"])
def Taipei_navigate():
    # with tracer.start_active_span('tourism') as scope:
        # scope.span.log_kv({'message': 'this is Taipei'})
        # #scope.span.set_tag('location','Taipei')
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)
        logger.info('GET: 200 /Taipei/ '+'traceid: '+trace_id+' spanid: '+span_id)
        
        return render_template('taipei.html')
@app.route('/Yilan',methods=["GET"])
def Yilan_navigate():
    # with tracer.start_active_span('tourism') as scope:
        # scope.span.log_kv({'message': 'this is Yilan'})
        # #scope.span.set_tag('location','Yilan')
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)
        logger.info('GET: 200 /Yilan '+'traceid: '+trace_id+' spanid: '+span_id)
        return render_template('Yilan.html')
@app.route('/Hualien',methods=["GET","POST"])
def Hualien_navigate():
    # with tracer.start_active_span('tourism') as scope:
        #scope.span.set_tag('location','Yilan')
        # add child span for tourism as scope 
        # span = trace.get_current_span()
        # if span is not None:
        #     trace_id = span.context.__getnewargs__()[0]
        #     span_id = span.context.__getnewargs__()[1]
        #     print(trace_id,span_id)
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)
        logger.info('GET: 200 /Hualien '+'traceid: '+trace_id+' spanid: '+span_id)
        if request.method == "POST":
            if request.form['s'] == "確定":
                fig_store.set = True
            elif request.form['s'] == "送出":
                value = request.form.get('OrderDay')
                Value.string = value
                click_store.set = True
            elif request.form['s'] == "寄出":
                url = "https://www.google.com/search?q="+"花蓮"+Value.Value_back()
                # with tracer.start_active_span('send_email',child_of='tourism') as scope:
                tour=crawl(url).tour_guide(url)
                Email = request.form.get('email')
                pack = [app,tour,Email]
                try:
                    SendEmail(pack).send_email(pack)
                    logger.info('GET: 200 /Hualien sending recommendation emails to users'
                        +' traceid: '+trace_id+' spanid: '+span_id)
                except:
                    logger.warn('Fail /Hualien sending recommendation emails to users'
                        +' traceid: '+trace_id+' spanid: '+span_id)
            else:
                value = request.form.get('OrderDay')
                if value == "親子友善":
                    url = 'https://www.google.com/travel/things-to-do/see-all?dest_mid=%2Fg%2F11clhptb5_&dest_state_type=sattd&dest_src=yts&q=%E8%8A%B1%E8%93%AE&ved=0CAAQ8IAIahcKEwj4pI2mhIT5AhUAAAAAHQAAAAAQCg&rf=Eh8KDS9nLzExYzcxaHZmdDASDOimquWtkOWPi-WWhCgB'
                elif value == "戶外活動":
                    url = 'https://www.google.com/travel/things-to-do/see-all?dest_mid=%2Fg%2F11clhptb5_&dest_state_type=sattd&dest_src=yts&q=%E8%8A%B1%E8%93%AE&ved=0CAAQ8IAIahcKEwj4pI2mhIT5AhUAAAAAHQAAAAAQCg&rf=Eh8KDS9nLzExYmM1OGwxM3cSDOaItuWklua0u-WLlSgB'
                elif value == "藝術與文化":
                    url ='https://www.google.com/travel/things-to-do/see-all?dest_mid=%2Fg%2F11clhptb5_&dest_state_type=sattd&dest_src=yts&q=%E8%8A%B1%E8%93%AE&ved=0CAAQ8IAIahcKEwj4pI2mhIT5AhUAAAAAHQAAAAAQCg&rf=EhwKBy9tLzBqancSD-iXneihk-iIh-aWh-WMligB'
                elif value == "歷史":
                    url = 'https://www.google.com/travel/things-to-do/see-all?dest_mid=%2Fg%2F11clhptb5_&dest_state_type=sattd&dest_src=yts&q=%E8%8A%B1%E8%93%AE&ved=0CAAQ8IAIahcKEwj4pI2mhIT5AhUAAAAAHQAAAAAQCg&rf=EhQKCC9tLzAzZzN3Egbmrbflj7IoAQ'
                elif value == "海灘":
                    url = 'https://www.google.com/travel/things-to-do/see-all?dest_mid=%2Fm%2F025c70&dest_state_type=main&dest_src=yts&rf=EgwKCC9tLzBiM3lyKAE&q=%E8%8A%B1%E8%93%AE%E6%B5%B7%E7%81%98&ved=0CAAQ8IAIahgKEwig1r3ChIT5AhUAAAAAHQAAAAAQnAM&tcfs=EhcKDS9nLzExY2xocHRiNV8SBuiKseiTrg'
                # with tracer.start_active_span('characteristic_tour',child_of='tourism') as scope:
                    # #scope.span.set_tag('character',value)
                try:
                    fig_stars = crawl(url).google_search(url)
                    logger.info('GET: 200 /Hualien crawling items to users'
                        +' traceid: '+trace_id+' spanid: '+span_id)
                except:
                    logger.warn('Fail /Hualien sending recommendation emails to users'
                        +' traceid: '+trace_id+' spanid: '+span_id)
                fig_store.fig = fig_stars
            # scope.span.log_kv({'message': 'this is Hualien'})
            return render_template('Hualien.html',figstars = fig_store.fig_back(),click=fig_store.set_back(),send_click = click_store.set_back())       
                    # redirect(url_for('Hualien_lookup',another = another))  
        else:
            # scope.span.log_kv({'message': 'this is Hualien'})
            return render_template('Hualien.html') 
@app.route('/Hualien/google/<name>', methods=["GET"])
def Hualien_google(name):
    # with tracer.start_active_span('google',child_of='characteristic_tour') as scope:
        # scope.span.log_kv({'event': 'google_search'})
        # span = trace.get_current_span()
        # if span is not None:
        #     trace_id = span.context.__getnewargs__()[0]
        #     span_id = span.context.__getnewargs__()[1]
        #     print(trace_id,span_id)
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/google/<name> '+'traceid: '+trace_id+' spanid: '+span_id)
        address = "https://www.google.com/search?q="+name
        return redirect(address)
@app.route('/Hualien/spot/', methods=["GET","POST"])
def Hualien_spot():
    # data = cur.execute("SELECT * FROM image WHERE loc='花蓮市'")
    data = Todo.query.filter_by(loc='花蓮市').all()
    # span = trace.get_current_span()
    # if span is not None:
    #     trace_id = span.context.__getnewargs__()[0]
    #     span_id = span.context.__getnewargs__()[1]
    #     print(trace_id,span_id)
    span = trace.get_current_span()
    trace_id,span_id = GetTraceSpanID(span)  
    logger.info('GET: 200 /Hualien/spot '+'traceid: '+trace_id+' spanid: '+span_id)

    if request.method == "POST":
        # with tracer.start_active_span('Hualien_city_spot',child_of='tourism') as scope:
            # scope.span.log_kv({'event':'lookup_all_hualien'})
            # scope.span.log_kv({'event':'post'})
            another = []
            task_content = request.form['content']
            logger.info('POST: 200 /Hualien/spot FilterAll'+'traceid: '+trace_id+' spanid: '+span_id)
            for todo in Todo.query.all():  
            # for todo in cur.execute("SELECT * FROM image"):  
                if todo.title == task_content:
                    another.append(todo.id)
            return redirect(url_for('Hualien_lookup',another = another))
    else: 
        # copy_data = Todo.query.all()
        # if len(another) != 0 :
        #     return render_template('Hualien_spot.html',data = another)
        # else: 
        #     print(copy_data,file=sys.stderr)
        #     return render_template('Hualien_spot.html',data = copy_data)
        # with tracer.start_active_span('Hualien_city_spot',child_of='tourism') as scope:
            # scope.span.log_kv({'message':'print_all_hualiencity_spot'})
            # scope.span.log_kv({'event':'get'})
            return render_template('Hualien_spot.html',data = data)

@app.route('/Hualien/spot/loc',methods=["GET","POST"])
def Hualien_lookup():
    # with tracer.start_active_span('lookup',child_of='Hualien_city_spot') as scope:
        data = []
        keys = request.args.get('another')
        ans = Todo.query.get_or_404(keys)
        data.append(ans)
        # scope.span.log_kv({'message':'location_lookup'})
        # scope.span.log_kv({'event':'get_loc'})
        # span = trace.get_current_span()
        # if span is not None:
        #     trace_id = span.context.__getnewargs__()[0]
        #     span_id = span.context.__getnewargs__()[1]
        #     print(trace_id,span_id)
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/spot/loc '+'traceid: '+trace_id+' spanid: '+span_id)
        return render_template('Hualien_spot.html',data = data)
@app.route('/Hualien/hotel',methods=["GET"])
def Hualien_hotel():
    # with tracer.start_active_span('Hualien_hotel',child_of='Hualien_city_spot'):
        url = 'https://www.booking.com/searchresults.zh-tw.html?label=gen173nr-1DCAEoggI46AdIM1gEaOcBiAEBmAEwuAEXyAEM2AED6AEBiAIBqAIDuAK7zuCWBsACAdICJDcyNDQyZWYxLWY2OTktNGJhZC1iNjEzLTE1NjM0OTFlOTg5MtgCBOACAQ&sid=80c3dd2e865839ba50f84a6b88e186fd&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.zh-tw.html%3Flabel%3Dgen173nr-1DCAEoggI46AdIM1gEaOcBiAEBmAEwuAEXyAEM2AED6AEBiAIBqAIDuAK7zuCWBsACAdICJDcyNDQyZWYxLWY2OTktNGJhZC1iNjEzLTE1NjM0OTFlOTg5MtgCBOACAQ%26sid%3D80c3dd2e865839ba50f84a6b88e186fd%26sb_price_type%3Dtotal%26%26&ss=%E8%8A%B1%E8%93%AE&is_ski_area=0&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&ss_raw=%E8%8A%B1%E8%93%AE&search_pageview_id=f57570de8fad009e'
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 booking /Hualien/hotel '+'traceid: '+trace_id+' spanid: '+span_id)
        return redirect(url)
@app.route('/Hualien/food',methods=["GET"])
def Hualien_food():
    # with tracer.start_active_span('Hualien_food',child_of='Hualien_city_spot'):
        # span = opentracing.tracer.active_span
        # if span is not None:
        #     trace_id = span.context.trace_id
        #     span_id = span.context.span_id
        # span = trace.get_current_span()
        # if span is not None:
        #     trace_id = span.context.__getnewargs__()[0]
        #     span_id = span.context.__getnewargs__()[1]
        #     print(trace_id,span_id)
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/food '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_food.html')
@app.route('/Hualien/transportation',methods=["GET"])
def Hualien_traffic():
    # with tracer.start_active_span('Hualien_traffic',child_of='Hualien_city_spot'):
        # span = opentracing.tracer.active_span
        # if span is not None:
        #     trace_id = span.context.trace_id
        #     span_id = span.context.span_id
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/transportation '+'traceid: '+trace_id+' spanid: '+span_id)
    
        url = 'https://www.funhualien.com.tw/hualien-traffic'
        return redirect(url)

##################
# 這邊是 li flag裡面的 a tag超連結設定
##################
@app.route('/Hualien/全部',methods=["GET"])
def all_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','全部')
        result = Todo.query.all() #已 return全部的花蓮市景點加入進來
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/全部 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)

@app.route('/Hualien/花蓮市',methods=["GET"])
def hualien_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','花蓮市')
        result = Todo.query.filter_by(loc='花蓮市').all() #已 return全部的花蓮市景點加入進來
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/花蓮市 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)

@app.route('/Hualien/玉里鎮',methods=["GET"])
def yuli_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','玉里鎮')
        result = Todo.query.filter_by(loc='玉里鎮').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/玉里鎮 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/光復鄉',methods=["GET"])
def kongfu_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','光復鄉')
        result = Todo.query.filter_by(loc='光復鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/光復鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/吉安鄉',methods=["GET"])
def jian_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','吉安鄉')
        result = Todo.query.filter_by(loc='吉安鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/吉安鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/秀林鄉',methods=["GET"])
def hsulin_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','秀林鄉')
        result = Todo.query.filter_by(loc='秀林鄉').all()
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/秀林鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/富里鄉',methods=["GET"])
def fuli_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','富里鄉')
        result = Todo.query.filter_by(loc='富里鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/富里鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/新城鄉',methods=["GET"])
def shinchen_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','新城鄉')
        result = Todo.query.filter_by(loc='新城鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/新城鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
    
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/瑞穗鄉',methods=["GET"])
def resei_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','瑞穗鄉')
        result = Todo.query.filter_by(loc='瑞穗鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/瑞穗鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/萬榮鄉',methods=["GET"])
def vanlung_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','萬榮鄉')
        result = Todo.query.filter_by(loc='萬榮鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/萬榮鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/壽豐鄉',methods=["GET"])
def shufun_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        result = Todo.query.filter_by(loc='壽豐鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/壽豐鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
        
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/鳳林鎮',methods=["GET"])
def vanlin_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','鳳林鎮')
        result = Todo.query.filter_by(loc='鳳林鎮').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/鳳林鎮 '+'traceid: '+trace_id+' spanid: '+span_id)
        
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/豐濱鄉',methods=["GET"])
def fungbin_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','豐濱鄉')
        result = Todo.query.filter_by(loc='豐濱鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/豐濱鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
        
        return render_template('Hualien_spot.html',data = result)
@app.route('/Hualien/卓溪鄉',methods=["GET"])
def jushi_lookup():
    #with tracer.start_active_span('Hualien_city_spot',child_of='lookup') as scope:
        #scope.span.set_tag('where','卓溪鄉')
        result = Todo.query.filter_by(loc='卓溪鄉').all() 
        span = trace.get_current_span()
        trace_id,span_id = GetTraceSpanID(span)  
        logger.info('GET: 200 /Hualien/卓溪鄉 '+'traceid: '+trace_id+' spanid: '+span_id)
        
        return render_template('Hualien_spot.html',data = result)
        
        
##################
# 這邊是 li flag裡面的 a tag超連結設定
##################

#各個景點介紹: 

@app.route('/<title>/<link_name>',methods=["GET"])
def plot_routing(link_name,title):
    #with tracer.start_active_span('Hualien_intro',child_of='Hualien_city_spot') as scope:
    #    scope.span.log_kv({'message':'location_intordoction'})
    #    scope.span.log_kv({'event':'location_intordoction'})
        link_name = "https://www.travelking.com.tw/tourguide/hualien/" + link_name
        try:
            data = crawl(link_name)
            data = data.data(link_name)
            data.append(title)
            data.append(len(data))
            store.List = data 
            
            span = trace.get_current_span()
            trace_id,span_id = GetTraceSpanID(span)  
            logger.info('GET: 200 /<title>/<link_name> '+'traceid: '+trace_id+' spanid: '+span_id)
            
            return render_template('introduction.html',data = data,set = False)
        except: 
            logger.error('/<title>/<link_name> crawling failed  '+'traceid: '+trace_id+' spanid: '+span_id)
            

@app.route('/booking/<variable>')
def booking(variable):
    #with tracer.start_active_span('Hualien_booking',child_of='Hualien_city_spot') as scope:
    #    scope.span.log_kv({'message':'booking_for_Hualien'})
        data = store.list_back()
        variable = re.sub('[a-zA-Z]',"",variable)
        variable = re.sub('[1-9]',"",variable)
        try:
            sel = selenium(variable).data(variable)
            span = trace.get_current_span()
            trace_id,span_id = GetTraceSpanID(span)  
            logger.info('GET: 200 /booking/<variable> '+'traceid: '+trace_id+' spanid: '+span_id)
            
            text = "為您推薦五筆優質旅館"
            return render_template('introduction.html',data = data,sel=sel,text =text,set=True)
        except:
            logger.fatal('---your selenium crawling is malfunctioning'+trace_id+'---')
        
if __name__ =='__main__':
    # print(Todo.query().filter_by(loc='花蓮市').all(),sys.stderr)
    # app.run(host="0.0.0.0",port=80,debug=True,use_reloadr=False)
    app.run(host="0.0.0.0",port=80,debug=True)
    # db.create_all() 
    # Init()
    # res= Todo.query().filter_by(loc='花蓮市').all()
    # print(res,sys.stderr)
