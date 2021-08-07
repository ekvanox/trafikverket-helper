import requests

class TrafikverketAPI:
    def __init__(self, cookies, proxy:dict, useragent:str, SSN:str, licence_ID:int=5, booking_mode_id:int=0,ignore_debt:bool=False, ignore_booking_hindrance:bool=False, examination_type_id:int=12,exclude_examination_categories:list=[], reschedule_type_id:int=0,payment_is_active:bool=False, payment_refrence:str=None,payment_url:str=None, searched_months:int=0,starting_date:str="1970-01-01T00:00:00.000Z",nearby_location_ids:list=[],vehicle_type_id:int=2,tachograph_id:int=1,occasion_choice_id:int=1) -> None:
        self.proxy = proxy
        self.session = requests.session()
        self.default_params = {"bookingSession":{"socialSecurityNumber":SSN,"licenceId":licence_ID,"bookingModeId":booking_mode_id,"ignoreDebt":ignore_debt,"ignoreBookingHindrance":ignore_booking_hindrance,"examinationTypeId":examination_type_id,"excludeExaminationCategories":exclude_examination_categories,"rescheduleTypeId":reschedule_type_id,"paymentIsActive":payment_is_active,"paymentReference":payment_refrence,"paymentUrl":payment_url,"searchedMonths":searched_months},"occasionBundleQuery":{"startDate":starting_date,"searchedMonths":searched_months,"locationId":None,"nearbyLocationIds":nearby_location_ids,"vehicleTypeId":vehicle_type_id,"tachographTypeId":tachograph_id,"occasionChoiceId":occasion_choice_id,"examinationTypeId":examination_type_id}}

        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)
        self.session.headers = {'Host': 'fp.trafikverket.se',
                    'Connection': 'keep-alive',
                    'Content-Length': '0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': useragent,
                    'Content-Type': 'application/json',
                    'Origin': 'https://fp.trafikverket.se',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://fp.trafikverket.se/Boka/',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',}

    def get_available_dates(self, location_id:int, extended_information:bool=False):
        # Update location ID from default params
        params = self.default_params
        params['occasionBundleQuery']['locationId'] = location_id

        # Send request to server
        r = self.session.post(url='https://fp.trafikverket.se/Boka/occasion-bundles', json=params, verify=False, proxies=self.proxy, timeout=60)

        # Handle response
        if r.status_code == 200 and (response_data:=r.json())['status'] == 200:
            # Extract data from response
            available_rides = response_data['data']['bundles']
            dates_found = [ride['occasions'][0]['date'] for ride in available_rides]

            if extended_information:
                return available_rides
            else:
                return dates_found
        else:
            raise Exception('Unexpected server response code')