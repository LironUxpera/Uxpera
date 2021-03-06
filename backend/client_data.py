class ClientData:
    def __init__(self, client):
        self.client = client

        self.dp_events = []
        self.bh_events = []
        self.nb_events = []
        self.sl_events = []
        self.sb_events = []

        # self.dp_events = ['search', 'search_bar', 'Product_Viewed']
        # self.bh_events = ['Clicked_Banner', 'promotions']
        # self.nb_events = ['hp_banner_custom']
        # self.sl_events = ['new_arrivals', 'best_sellers']
        # self.sb_events = ['reviews', 'timeout', 'terms_and_cond', 'security_and_priv', 'about_us', 'browsing_no_click',
        #                   'Scrolling_To_Second_Part', 'scrolling_to_third']

        self.long_time_events = []
        self.timeout_events = []
        self.scroll_events = []
        self.no_time_limit_events = []

        # load the behavior mapping, copy & cta tables
        self.behavior_mapping_df = None
        self.products_df = None
        self.best_sellers_df = None
        self.copy4_df = None
        self.copy2_df = None
        self.cta_df = None
        self._load_data_tables()

        # load the client banners
        self.desktop_hp_testimonial_banner = ''
        self.desktop_hp_promotional_banner = ''
        self.mobile_hp_testimonial_banner = ''
        self.mobile_hp_promotional_banner = ''

        self.desktop_pp_testimonial_banner = ''
        self.desktop_pp_promotional_banner = ''
        self.mobile_pp_promotional_banner = ''

        self.desktop_cp_testimonial_banner = ''
        self.desktop_cp_promotional_banner = ''
        self.mobile_cp_promotional_banner = ''

        self._load_banners()

    def _load_data_tables(self):
        pass

    def _load_banners(self):
        pass

    def _get_canonical_event_type(self, event):
        return event.event_type

    def _check_plain_behaviour(self, last_type):
        if last_type in self.dp_events:
            return 'DP'
        elif last_type in self.bh_events:
            return 'BH'
        elif last_type in self.nb_events:
            return 'NBS'
        elif last_type in self.sl_events:
            return 'SL'
        elif last_type in self.sb_events or last_type in self.long_time_events:
            return 'SB'
        elif last_type in self.timeout_events:
            return 'SB'

    def check_behaviour(self, user):
        """this method not only checks the behaviour based on rules but also has side effects on User"""

        behaviour = None

        print('$$$$$')
        print('Checking behaviour')
        session_start_time = user.get_session_start_time()
        events = user.get_events()
        if not events:
            return behaviour

        print('Checking behaviour - have events')
        last_event = events[-1]
        last_time = last_event.time - session_start_time
        last_type = self._get_canonical_event_type(last_event)
        sessions = user.get_ssession_num()
        print(f'== Session={sessions} Checking time={last_time} event={last_type}')
        current_assumed_behavior = user.get_behaviour()

        # check if scroll event and give extra time
        if user.get_extra_time_mode():
            # give extra 15s
            last_time -= 15000
        if last_type in self.scroll_events:
            user.set_extra_time_mode()
            # TODO Harry: why do we continue here ....

        plain_behaviour = self._check_plain_behaviour(last_type)

        if sessions == 1:
            # handle not time limit mode checking and setting
            if user.get_no_time_limit_mode():
                return plain_behaviour
            elif last_type in self.no_time_limit_events:
                user.set_no_time_limit_mode()
                return

            if last_time <= 21000:
                if last_type in self.timeout_events:
                    print(f'== timeout event')
                    behaviour = 'SB'

            if last_time <= 15000:
                if last_type in self.long_time_events:
                    print(f'== Long time event')
                    behaviour = 'SB'

            # left check for events in first 5 seconds
            if last_time <= 10000:
                if last_type in self.dp_events:
                    behaviour = 'DP'
                elif last_type in self.bh_events:
                    behaviour = 'BH'
                elif last_type in self.nb_events:
                    behaviour = 'NBS'
                elif last_type in self.sl_events:
                    behaviour = 'SL'
                elif last_type in self.sb_events:
                    behaviour = 'SB'

        else:
            # 2 or more sessions
            if current_assumed_behavior == 'DP' and not user.get_bought_last_session():
                print(f'== 2 or more sessions - Case 1')
                user.set_behaviour_changed()
                user.set_behaviour_escalated()
                behaviour = 'NBS'
            elif plain_behaviour != current_assumed_behavior:
                # checking if we have a contradicted event
                if len(events) == 2:
                    # if first event after start is a contradiction then remember it
                    user.set_contradicted_behaviour(plain_behaviour)
                elif user.get_contradicted_behaviour() is not None and len(events) == 3:
                    print(f'== 2 or more sessions - Case 2')
                    # if 2 first events are a contradiction then use the first one
                    user.set_behaviour_changed()
                    user.set_behaviour_escalated()
                    behaviour = user.get_contradicted_behaviour()
            elif sessions >= 3 and (current_assumed_behavior == 'SL' or current_assumed_behavior == 'BH') \
                    and not user.get_bought_anything():
                print(f'== 2 or more sessions - Case 3')
                user.set_behaviour_changed()
                user.set_behaviour_escalated()
                behaviour = 'NBS'
            elif sessions == 4 and current_assumed_behavior == 'NBS' and not user.get_bought_anything():
                print(f'== 2 or more sessions - Case 3')
                user.set_behaviour_changed()
                user.set_behaviour_escalated()
                behaviour = 'SB'

        return behaviour

    def _get_random_best_seller(self):
        return None

    def _get_product_info(self, prod_id):
        return '', '', ''

    def _get_cta_id_for_behaviour(self, behaviour):
        return None

    def _get_cta_for_cta_id(self, cta_id):
        return ''

    def _get_copy4_for_prod_id(self, prod_id):
        return '', '', '', '', ''

    def _get_copy2_for_prod_id(self, prod_id):
        return '', '', ''

    def calc_banner(self, assumed_behaviour, page_type, is_mobile):
        return None
