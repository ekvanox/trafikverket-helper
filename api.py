import requests


class TrafikverketAPI:
    def __init__(
        self,
        cookies,
        proxy: dict,
        useragent: str,
        ssn: str,
        licence_ID: int = 5,
        booking_mode_id: int = 0,
        ignore_debt: bool = False,
        ignore_booking_hindrance: bool = False,
        examination_type_id: int = 12,
        exclude_examination_categories: list = [],
        reschedule_type_id: int = 0,
        payment_is_active: bool = False,
        payment_refrence: str = None,
        payment_url: str = None,
        searched_months: int = 0,
        starting_date: str = "1970-01-01T00:00:00.000Z",
        nearby_location_ids: list = [],
        vehicle_type_id: int = 2,
        tachograph_id: int = 1,
        occasion_choice_id: int = 1
    ) -> None:
        """
        Initialize a TrafikverketAPI object.

        Args:
            cookies: A dictionary containing the cookies for the session.
            proxy: A dictionary containing the proxy settings for the session.
            useragent: A string containing the user agent for the session.
            SSN: A string containing the user's SSN.
            licence_ID: An integer specifying the user's licence ID. Defaults to 5.
            booking_mode_id: An integer specifying the booking mode ID. Defaults to 0.
            ignore_debt: A boolean indicating whether to ignore any outstanding debts. Defaults to False.
            ignore_booking_hindrance: A boolean indicating whether to ignore any booking hindrances. Defaults to False.
            examination_type_id: An integer specifying the examination type ID. Defaults to 12.
            exclude_examination_categories: A list of integers specifying the examination categories to exclude. Defaults to an empty list.
            reschedule_type_id: An integer specifying the reschedule type ID. Defaults to 0.
            payment_is_active: A boolean indicating whether payment is active. Defaults to False.
            payment_refrence: A string containing the payment reference. Defaults to None.
            payment_url: A string containing the payment URL. Defaults to None.
            searched_months: An integer specifying the number of months to search. Defaults to 0.
            starting_date: A string specifying the starting date in the format "YYYY-MM-DDTHH:MM:SS.000Z". Defaults to "1970-01-01T00:00:00.000Z".
            nearby_location_ids: A list of integers specifying the nearby location IDs. Defaults to an empty list.
            vehicle_type_id: An integer specifying the vehicle type ID. Defaults to 2.
            tachograph_id: An integer specifying the tachograph type ID. Defaults to 1.
            occasion_choice_id: An integer specifying the occasion choice ID. Defaults to 1.
        """

        # Set the proxy settings
        self.proxy = proxy

        # Create a new session
        self.session = requests.session()

        # Set the default parameters for the API calls
        self.default_params = {
            "bookingSession": {
                "socialSecurityNumber": ssn,
                "licenceId": licence_ID,
                "bookingModeId": booking_mode_id,
                "ignoreDebt": ignore_debt,
                "ignoreBookingHindrance": ignore_booking_hindrance,
                "examinationTypeId": examination_type_id,
                "excludeExaminationCategories": exclude_examination_categories,
                "rescheduleTypeId": reschedule_type_id,
                "paymentIsActive": payment_is_active,
                "paymentReference": payment_refrence,
                "paymentUrl": payment_url,
                "searchedMonths": searched_months
            },
            "occasionBundleQuery": {
                "startDate": starting_date,
                "searchedMonths": searched_months,
                "locationId": None,
                "nearbyLocationIds": nearby_location_ids,
                "vehicleTypeId": vehicle_type_id,
                "tachographTypeId": tachograph_id,
                "occasionChoiceId": occasion_choice_id,
                "examinationTypeId": examination_type_id
            }
        }

        # Add the cookies to the session's cookiejar
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)

        # Set the headers for the session
        self.session.headers = {
            'Host': 'fp.trafikverket.se',
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
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def get_available_dates(self, location_id: int, extended_information: bool = False) -> list[dict] | list[str]:
        """
        Retrieve a list of available dates for the given location.

        Args:
            location_id: The ID of the location to query.
            extended_information: If True, return detailed information about the
                available dates, including the time and the occasion ID. Otherwise,
                return only the date as a string in the format 'YYYY-MM-DD'.

        Returns:
            If extended_information is True, a list of dictionaries containing the
            details of the available dates. Otherwise, a list of strings representing
            the available dates.

        Raises:
            Exception: If the server returns an unexpected response code.
        """
        # Update location ID from default params
        params = self.default_params
        params['occasionBundleQuery']['locationId'] = location_id

        # Send request to server
        r = self.session.post(
            url='https://fp.trafikverket.se/Boka/occasion-bundles',
            json=params,
            verify=False,
            proxies=self.proxy,
            timeout=60
        )

        # Handle response
        if r.status_code == 200 and (response_data := r.json())['status'] == 200:
            # Extract data from response
            available_rides = response_data['data']['bundles']
            dates_found = [
                ride['occasions'][0]['date'] for ride in available_rides
            ]

            # Return the dates found or the full list of available rides,
            # depending on the value of the extended_information flag.
            if extended_information:
                return available_rides
            else:
                return dates_found
        else:
            raise Exception('Unexpected server response code')
