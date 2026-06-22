# run.py by Fleur van Teijlingen
# In combination with mission_manager.py and flight_patterns.py
# Used for running different experiments as defined in flight_patterns.py

import logging
import sys
import time
import cflib.crtp
import sys
import yaml
import itertools
from datetime import datetime
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from mission_manager import MissionManager

URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
logging.basicConfig(level=logging.ERROR)

    
def load_matrix_config():
    """
    Loads yaml file: one for each experiment. 
    Has platform, deck, experiment, height, distance, speed as parameters
    """
    if len(sys.argv) < 2:
        print("Error: no YAML file")
        sys.exit(1)
    with open(sys.argv[1], 'r') as file:
        return yaml.safe_load(file)


if __name__ == '__main__':
    config = load_matrix_config()
    active = config['active_setup']
    PLATFORM = active['platform']
    DECK = active['deck']
    EXPERIMENT = active['experiment']
    
    matrix = config['matrix']
    distances = matrix['distances']
    heights = matrix['heights']
    speeds = matrix['speeds']
    repetitions = matrix['repetitions']
    
    # calculates all runs
    all_runs = list(itertools.product(distances, heights, speeds, range(1, repetitions + 1)))
    
    print(f"\n=========================================")
    print(f" Configuration loaded: {len(all_runs)} flights generated.")
    print(f" Experiment: {EXPERIMENT} op {PLATFORM} ({DECK})")
    print(f"=========================================")
    
    ans = input(f" Start with {len(all_runs)} flights? ")
    if ans.lower() not in ['y', 'yes', 'ja', 'j', '1']:
        sys.exit(1)

    LighthouseActive = (DECK == 'bcLighthouse4')
    LocoActive = (DECK == 'bcLoco')
    cflib.crtp.init_drivers()

    for dist, height, speed, rep in all_runs:
        print(f" \n Next Run: Dist={dist}m | Height={height}m | Speed={speed}m/s | Repetition={rep}/{repetitions}")
        
        ready = input(" Press enter to start or (q)uit\n ")
        if ready.lower() in ['q', 'quit']:
            break
            
        date = datetime.now()
        filedate = date.strftime("%Y-%m-%d_%H-%M-%S")

        print("================ START ==================")

        mission = MissionManager(
            platform=PLATFORM, 
            deck=DECK,
            experiment=EXPERIMENT,
            time=filedate,
            default_distance=dist,
            default_height=height,
            default_speed=speed
        )

        # ms for loggings
        log_period = 10
    
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
            try:
                time.sleep(1)

                # ---------------------- LOGCONFIGS -------------------------------------
                logconf_pos = LogConfig(name='Position', period_in_ms=log_period)
                logconf_pos.add_variable('stateEstimate.x', 'float')
                logconf_pos.add_variable('stateEstimate.y', 'float')
                logconf_pos.add_variable('stateEstimate.z', 'float')
                logconf_pos.add_variable('stateEstimate.roll', 'float')
                logconf_pos.add_variable('stateEstimate.pitch', 'float')
                logconf_pos.add_variable('stateEstimate.yaw', 'float')

                vbat_log = LogConfig(name='BatteryCheck', period_in_ms=100)
                vbat_log.add_variable('pm.vbat', 'float')

                logconf_kal = LogConfig(name='KalmanVariance', period_in_ms=log_period)
                logconf_kal.add_variable('kalman.varPX', 'float')
                logconf_kal.add_variable('kalman.varPY', 'float')
                logconf_kal.add_variable('kalman.varPZ', 'float')
                logconf_kal.add_variable('kalman.varX', 'float')
                logconf_kal.add_variable('kalman.varY', 'float')
                logconf_kal.add_variable('kalman.varZ', 'float')

                logconf_vel = LogConfig(name='Velocity', period_in_ms=log_period)
                logconf_vel.add_variable('stateEstimate.vx', 'float')
                logconf_vel.add_variable('stateEstimate.vy', 'float')
                logconf_vel.add_variable('stateEstimate.vz', 'float')
                logconf_vel.add_variable('ctrltarget.vx', 'float')
                logconf_vel.add_variable('ctrltarget.vy', 'float')
                logconf_vel.add_variable('ctrltarget.vz', 'float')

                logconf_cont = LogConfig(name='ControlVariables', period_in_ms=log_period)
                logconf_cont.add_variable('ctrltarget.x', 'float')
                logconf_cont.add_variable('ctrltarget.y', 'float')
                logconf_cont.add_variable('ctrltarget.z', 'float')


                # adds lighthouse and loco parameters
                if LighthouseActive:
                    logconf_light = LogConfig(name='Lighthouse', period_in_ms=log_period)
                    logconf_light.add_variable('lighthouse.status', 'float')
                    logconf_light.add_variable('lighthouse.bsReceive', 'float')
                elif LocoActive:
                    logconf_loco1 = LogConfig(name='Loco', period_in_ms=log_period)
                    logconf_loco1.add_variable('ranging.distance0', 'float')
                    logconf_loco1.add_variable('ranging.distance1', 'float')
                    logconf_loco1.add_variable('ranging.distance2', 'float')
                    logconf_loco1.add_variable('ranging.distance3', 'float')

                    logconf_loco2 = LogConfig(name='Loco2', period_in_ms=log_period)
                    logconf_loco2.add_variable('ranging.distance4', 'float')
                    logconf_loco2.add_variable('ranging.distance5', 'float')
                    logconf_loco2.add_variable('ranging.distance6', 'float')
                    logconf_loco2.add_variable('ranging.distance7', 'float')
                    
            
                # adds logging to configuration
                scf.cf.log.add_config(vbat_log)
                scf.cf.log.add_config(logconf_cont)
                scf.cf.log.add_config(logconf_pos)
                scf.cf.log.add_config(logconf_vel)
                scf.cf.log.add_config(logconf_kal)


                # asks for update
                if LighthouseActive:
                    scf.cf.log.add_config(logconf_light)
                    logconf_light.data_received_cb.add_callback(mission.log_lighthouse)

                elif LocoActive:
                    scf.cf.log.add_config(logconf_loco1)
                    scf.cf.log.add_config(logconf_loco2)
                    logconf_loco1.data_received_cb.add_callback(mission.log_loco1)
                    logconf_loco2.data_received_cb.add_callback(mission.log_loco2)

                logconf_kal.data_received_cb.add_callback(mission.log_kalman)
                logconf_cont.data_received_cb.add_callback(mission.log_control)
                vbat_log.data_received_cb.add_callback(mission.log_battery)
                logconf_pos.data_received_cb.add_callback(mission.log_position)
                logconf_vel.data_received_cb.add_callback(mission.log_velocity)

                # ---------------------- HARDWARE CHECKUPS -------------------------------
                vbat_log.start()

                # checks for deck
                scf.cf.param.add_update_callback(group="deck", name=mission.deck, cb=mission.param_deck)
                scf.cf.param.request_param_update(f"deck.{mission.deck}")
                start_wait = time.time()
                while not mission.deck_attached_event.is_set():
                    time.sleep(0.1)
                    if time.time() - start_wait > 3.0:
                        print(f"ERROR: Correct deck ({mission.deck}) is NOT attached or not responding!")
                        sys.exit(1)
                time.sleep(1)

                # forces kalman filter to reset
                try:
                    scf.cf.param.set_value("kalman.resetEstimation", "1")
                    time.sleep(2.0)
                    print("Kalman filter reset")
                except Exception as ke:
                    print(f"Kalman filter failed {ke}")

                # ---------------------- START EXPERIMENT -------------------------------------
                scf.cf.platform.send_arming_request(False) 
                time.sleep(1)
                mission.start_csv()
                
                print("Start logging")
                logconf_cont.start()
                logconf_pos.start()
                logconf_kal.start()
                logconf_vel.start()
                if LighthouseActive:
                    logconf_light.start()
                elif LocoActive:
                    logconf_loco1.start()
                    logconf_loco2.start()

                print("Arming")
                scf.cf.platform.send_arming_request(True)
                time.sleep(0.5)          
                
                print("Flying")
                mission.perform_flight(scf)

            except Exception as e:
                print(f"Error: {e}")
            
            # ---------------------- SHUTTING DOWN -------------------------------------
            finally:
                # succes: flight was performed
                if mission.is_open:
                    print("Disarming")
                    scf.cf.platform.send_arming_request(False)

                    print("Stop logging")
                    logconf_pos.stop()
                    vbat_log.stop()
                    logconf_cont.stop()
                    logconf_kal.stop()
                    logconf_vel.stop()
                    if LighthouseActive:
                        logconf_light.stop()
                    elif LocoActive:
                        logconf_loco1.stop()
                        logconf_loco2.stop()
                    time.sleep(1)
                    
                    mission.close()
                    print(f"Saved in {mission.file_path}")

                    print("================ STOP ===================")
                else: 
                    print("Try again!") 

                scf.close_link() # very important! Enables multiple consequent script runs
