from pathlib import Path
import csv
from cflib.positioning.position_hl_commander import PositionHlCommander
import sys
import flight_patterns
from threading import Event
import time



class MissionManager:
    def __init__(self, platform: str, deck: str, experiment: str, time: str,  default_distance=1.5, default_height:int=0.5, default_speed=0.2):
        """
        Initializes current mission with platform, deck and experiment
        """
        self.platform = platform
        self.deck = deck
        self.time = time

        self.file_path = Path('data/bitcraze') / platform / deck[2:] / experiment / f"{platform[0]}{deck[2:5]}_{experiment}_D{default_distance}-H{default_height}-S{default_speed}_{time}.csv"
        self.experiment = experiment
        self.battery_printed = False
        self.current_vbat = 0.0
        self.is_open = False
        self.H = default_height
        self.V = default_speed
        self.D = default_distance
        self.deck_attached_event = Event()

        nan_val = float('nan')
        self.kx = nan_val
        self.ky = nan_val
        self.kz = nan_val
        self.kvx = nan_val
        self.kvy = nan_val
        self.kvz = nan_val
        self.vx = nan_val
        self.vy = nan_val
        self.vz = nan_val
        self.target_vx = nan_val
        self.target_vy = nan_val
        self.target_vz = nan_val
        self.lh_status = nan_val
        self.lh_receive = nan_val
        self.lc_rd0 = nan_val
        self.lc_rd1 = nan_val
        self.lc_rd2 = nan_val
        self.lc_rd3 = nan_val
        self.lc_rd4 = nan_val
        self.lc_rd5 = nan_val
        self.lc_rd6 = nan_val
        self.lc_rd7 = nan_val

    def start_csv(self):
        """
        Creates csv file for parameters
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_file = open(self.file_path, mode='w', newline='')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow([f"#Time:{self.time}, Platform:{self.platform}, Deck:{self.deck}, Experiment:{self.experiment}, Parameters: [H:{self.H}, D:{self.D}, V:{self.V}]"])        
        self.writer.writerow(['TimestampMS', 'TimeUnix', 'Vbat', 
                            'X', 'Y', 'Z',
                            'VarX', 'VarY', 'VarZ',
                            'TargetX', 'TargetY', 'TargetZ',
                            'Roll', 'Pitch', 'Yaw',
                            'VX', 'VY', 'VZ',
                            'VarPX', 'VarPY', 'VarPZ',
                            'TargetVX', 'TargetVY', 'TargetVZ',
                            'lhStatus', 'lhReceive', 
                            'lcRng0', 'lcRng1', 'lcRng2', 'lcRng3',
                            'lcRng4', 'lcRng5', 'lcRng6', 'lcRng7'])
        
        self.is_open = True

    def close(self):
        """
        Closes csv file
        """
        self.csv_file.close()
        self.is_open = False

    def param_deck(self, _, value_str):
        """
        Checks if correct deck is attached
        """
        value = int(value_str)
        if value:
            self.deck_attached_event.set()           

    def log_battery(self, timestamp, data, logconf):
        """ 
        Checks if battery is full enough for a flight
        """
        voltage = data['pm.vbat']
        self.current_vbat = voltage

        if voltage == 0.0:
            return
        
        # different voltage for different platform
        if self.platform == 'Flapper':
            MIN_BATTERY_VOLTAGE = 6.5
        elif self.platform == 'Crazyflie':
            MIN_BATTERY_VOLTAGE = 3.5
            
        # checks battery
        if not self.battery_printed:
            if voltage >= MIN_BATTERY_VOLTAGE:
                print(f'Battery level is good: {voltage:.2f}V')
                self.battery_printed = True
            else:
                print(f'ERROR: Battery too low ({voltage:.2f}V)!')
                sys.exit(1)

    def log_kalman(self, timestamp, data, logconf):
        """
        Logs Kalman variance for position and velocity
        """
        self.kx = data.get('kalman.varX', 0.0)
        self.ky = data.get('kalman.varY', 0.0)
        self.kz = data.get('kalman.varZ', 0.0)
        self.kvx = data.get('kalman.varPX', 0.0)
        self.kvy = data.get('kalman.varPY', 0.0)
        self.kvz = data.get('kalman.varPZ', 0.0)

    def log_velocity(self, timestamp, data, logconf):
        """
        Logs velocity and target velocity
        """
        self.vx = data.get('stateEstimate.vx', 0.0)
        self.vy = data.get('stateEstimate.vy', 0.0)
        self.vz = data.get('stateEstimate.vz', 0.0)
        self.target_vx = data.get('ctrltarget.vx', 0.0)
        self.target_vy = data.get('ctrltarget.vy', 0.0)
        self.target_vz = data.get('ctrltarget.vz', 0.0)

    def log_control(self, timestamp, data, logconf):
        """
        Logs target position
        """
        self.target_x = data.get('ctrltarget.x', 0.0)
        self.target_y = data.get('ctrltarget.y', 0.0)
        self.target_z = data.get('ctrltarget.z', 0.0)

    def log_lighthouse(self, timestamp, data, logconf):
        """
        Logs lighthouse status
        """
        self.lh_status = data.get('lighthouse.status', 0.0)
        self.lh_receive = data.get('lighthouse.bsReceive', 0.0)

    def log_loco1(self, timestamp, data, logconf):
        """
        Logs loco status top anchors
        """
        self.lc_rd0 = data.get('ranging.distance0', 0.0)
        self.lc_rd1 = data.get('ranging.distance1', 0.0)
        self.lc_rd2 = data.get('ranging.distance2', 0.0)
        self.lc_rd3 = data.get('ranging.distance3', 0.0)

    def log_loco2(self, timestamp, data, logconf):
        """
        Logs loco status bottom anchors
        """
        self.lc_rd4 = data.get('ranging.distance4', 0.0)
        self.lc_rd5 = data.get('ranging.distance5', 0.0)
        self.lc_rd6 = data.get('ranging.distance6', 0.0)
        self.lc_rd7 = data.get('ranging.distance7', 0.0)

    def log_position(self, timestamp, data, logconf):
        """
        Logs state estimation x, y and z, and roll, pitch and yaw.
        """
        self.x = data.get('stateEstimate.x', 0.0)
        self.y = data.get('stateEstimate.y', 0.0)
        self.z = data.get('stateEstimate.z', 0.0)
        self.roll = data.get('stateEstimate.roll', 0.0)
        self.pitch = data.get('stateEstimate.pitch', 0.0)
        self.yaw = data.get('stateEstimate.yaw', 0.0)

        logging_variables = [timestamp, time.time(), self.current_vbat, 
                                self.x, self.y, self.z,
                                self.kx, self.ky, self.kz,
                                self.target_x, self.target_y, self.target_z,
                                self.roll, self.pitch, self.yaw,
                                self.vx, self.vy, self.vz,
                                self.kvx, self.kvy, self.kvz,
                                self.target_vx, self.target_vy, self.target_vz
                                ]
        nan_val = float('nan')
        if self.deck=='bcLighthouse4':
            logging_variables += [self.lh_status, self.lh_receive] + [nan_val for _ in range(8)]
        elif self.deck=='bcLoco':
            logging_variables += [nan_val, nan_val, self.lc_rd0, self.lc_rd1, self.lc_rd2, self.lc_rd3, self.lc_rd4, self.lc_rd5, self.lc_rd6, self.lc_rd7]

        self.writer.writerow(logging_variables)

    def perform_flight(self, scf):
        """
        General function to call on experiment functions
        """
        # finds initial position through positioning system
        try:
            init_x = self.x
            init_y = self.y

        except Exception as e:
            # sets starting coordinate as origin
            print(f"Error: Set 0.0 automatically {e}")
            init_x = 0.0
            init_y = 0.0
      
        print(f"Executing {self.experiment}")
        experiment_name = self.experiment.lower() + "_flight"

        if experiment_name == 'motionless_flight':
            flight_patterns.motionless_flight()
        else:
            # uses high level commander for flight control - more precise than motion commander
            with PositionHlCommander(scf, x=init_x, y=init_y, default_height=self.H, default_velocity=self.V, default_landing_height=0.05, controller=PositionHlCommander.CONTROLLER_PID) as pc:
                try:
                    # finds flight pattern in flight_patterns.py
                    flight_function = getattr(flight_patterns, experiment_name)
                    flight_function(pc, distance=self.D, height=self.H, speed=self.V)
                except AttributeError:
                    print(f"ERROR: {self.experiment} does not exist!")
                    sys.exit(1)