import os
import threading
from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_restx import Api, ValidationError as ValidationErr
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
from smtplib import SMTPException
from flask_cors import CORS
from F_taste_misurazioni.db import set_DB_CONFIG,create_db
from F_taste_misurazioni.kafka.kafka_consumer import consume

from F_taste_misurazioni.ma import ma

from F_taste_misurazioni.namespaces import nutrizionista_ns,paziente_ns
from F_taste_misurazioni.controllers.misurazione_controller import MisurazioniController,MisurazionePazienteController,MisurazioniPazienteController
from F_taste_misurazioni.controllers.misurazione_medico_controller import MisurazioneMedicoController,MisurazioniMedicoPazienteController,MisurazioniMedicoController


from F_taste_misurazioni.utils.jwt_custom_decorators import NoAuthorizationException




#from flaskr.utils.redis import get_redis_connection, init_redis_connection_pool

from logging import getLogger

def start_kafka_consumer(app):
    thread = threading.Thread(target=consume,args=(app,) ,daemon=True)
    thread.start()

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('F_taste_misurazioni.config.DevelopmentConfig')

    
   

   #Parte di redis

   # if app.config['REDIS_HOST'] is None:
    #    app.config['REDIS_HOST'] = 'localhost'
    #if app.config['REDIS_PORT'] is None:
     #   app.config['REDIS_PORT'] = 6379

    with app.app_context():
    #    init_redis_connection_pool(app)
        create_db()

    if __name__ != '__main__':
        gunicorn_logger = getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    
    
    # teardown connection pool redis
   # @app.teardown_appcontext
    #def close_redis_connection(exception=None):
     #   redis = get_redis_connection()
      #  if redis is not None:
       #     redis.connection_pool.disconnect()


   

    CORS(app)
    api = Api(app, doc='/doc', title='rest api f-taste documentation')
    jwt = JWTManager(app)


    # controllo se token è in blacklist
  #  @jwt.token_in_blocklist_loader
   # def check_if_token_is_revoked(jwt_header, jwt_payload):
    #    if os.environ.get('FLASK_ENV') == "Test":
     #       return False
      #  jti = jwt_payload["jti"]
       # try:
        #    redis_connection = get_redis_connection()
        #except Exception as e:
         #   print(e)
          #  raise e
        #token_in_redis = redis_connection.get(jti)
        #return token_in_redis is not None

   # ma.init_app(app)

    #namespaces here
    api.add_namespace(nutrizionista_ns)
    api.add_namespace(paziente_ns)
    #adding CORS after request
    @app.after_request
    def add_header(response):
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        return response

    #errors handlers here
  #  @api.errorhandler(ValidationError)
   # def handle_validations_error(error: ValidationError):
    #    return {'message': 'An error in validation accoured'}, 400

#    @api.errorhandler(ValidationErr)
 #   def handle_validations_error(error: ValidationErr):
  #      return error, 400
        
 #   @api.errorhandler(NoResultFound)
  #  def handle_NoResultFound_error(error: NoResultFound):
   #     return {'message': str(error.args)}, 404


   # @api.errorhandler(SMTPException)
   # def handle_SMTPExceprion_error(error: SMTPException):
    #    return {'message': error.strerror}, 500

   # @api.errorhandler(NoAuthorizationException)
    #def handle_SMTPExceprion_error(error: NoAuthorizationException):
     #   return {'message': error.args}, 403
    

   

   
    nutrizionista_ns.add_resource(MisurazioniController, '/misurazioni_paziente')
    nutrizionista_ns.add_resource(MisurazioneMedicoController, '/misurazione_medico')
    nutrizionista_ns.add_resource(MisurazioniMedicoController, '/misurazioni_medico')

    paziente_ns.add_resource(MisurazioniMedicoPazienteController, '/misurazione_medico')
    paziente_ns.add_resource(MisurazioniPazienteController,'/misurazioni')
    paziente_ns.add_resource(MisurazionePazienteController,'/misurazione')

    

   
   
    
    

    


#    app.add_url_rule("/password_reset", view_func=TemplatePasswordChangerController.reindirizza, methods=['GET'])
 #   app.add_url_rule("/success", view_func=TemplatePasswordChangerController.successo, methods=['GET'])
  #  app.add_url_rule("/failure", view_func=TemplatePasswordChangerController.fallimento, methods=['GET'])
    
    @app.route('/health', methods=['GET'])#è solo per prova
    def health_check():
        return {'message': 'API misurazioni è online'}, 200
    
    # Avvia il Consumer Kafka all'avvio del servizio paziente
    start_kafka_consumer(app)
    
    return app