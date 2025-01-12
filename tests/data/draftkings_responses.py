"""Mock responses for DraftKings API tests."""

MOCK_EVENT_GROUP_RESPONSE = {
    "eventGroup": {
        "eventGroupId": 88670846,
        "name": "2024 NFL Draft",
        "events": [
            {
                "eventId": 123456,
                "name": "2024 NFL Draft - Player Draft Position",
                "offers": [
                    {
                        "label": "Draft Position Over/Under 5.5",
                        "outcomes": [
                            {
                                "label": "Caleb Williams - Over 5.5",
                                "oddsAmerican": "+150"
                            },
                            {
                                "label": "Caleb Williams - Under 5.5",
                                "oddsAmerican": "-180"
                            }
                        ]
                    },
                    {
                        "label": "First Round Draft Position",
                        "outcomes": [
                            {
                                "label": "Marvin Harrison Jr. - Pick 1",
                                "oddsAmerican": "+450"
                            },
                            {
                                "label": "Marvin Harrison Jr. - Pick 2",
                                "oddsAmerican": "+300"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

MOCK_ERROR_RESPONSE = {
    "error": "Internal Server Error",
    "status": 500
}

EXPECTED_PARSED_ODDS = [
    {
        "player_name": "Caleb Williams",
        "market_type": "Draft Position Over/Under 5.5",
        "odds": "+150",
        "draft_position": 5.5,
        "sportsbook": "DraftKings"
    },
    {
        "player_name": "Caleb Williams",
        "market_type": "Draft Position Over/Under 5.5",
        "odds": "-180",
        "draft_position": 5.5,
        "sportsbook": "DraftKings"
    },
    {
        "player_name": "Marvin Harrison Jr.",
        "market_type": "First Round Draft Position",
        "odds": "+450",
        "draft_position": 1.0,
        "sportsbook": "DraftKings"
    },
    {
        "player_name": "Marvin Harrison Jr.",
        "market_type": "First Round Draft Position",
        "odds": "+300",
        "draft_position": 2.0,
        "sportsbook": "DraftKings"
    }
] 