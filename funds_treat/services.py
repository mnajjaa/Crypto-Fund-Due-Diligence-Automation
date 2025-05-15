import requests

def fetch_project_data(symbol):
    """
    Fetches project data for a given coin symbol.
    Replace the URL and parameters with those required by your API.
    """
    url = f"https://api.example.com/crypto/{symbol}"  # Update with the real API endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Failed to fetch data for {symbol}"}

# data/services/fund_cache.py
import requests

FUND_CACHE = {}

def load_fund_cache():
    global FUND_CACHE
    if not FUND_CACHE:
        all_funds = []
        for offset in range(0, 1000, 100):
            res = requests.get("https://api.cryptorank.io/v0/funds/table/", params={"limit": 100, "offset": offset})
            if res.status_code == 200:
                all_funds.extend(res.json().get("data", []))
        FUND_CACHE = {fund.get("slug"): fund for fund in all_funds}
    return FUND_CACHE



########################Start of the FundAPITester class###########################

import requests
import html
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class FundAPITester:
    def __init__(self):
        self.base_url = "https://api.cryptorank.io/v0"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        self.timeout = 10


        # Add to the FundAPITester class
    def get_investments_by_country(self, slug: str, start_date: str, end_date: str):
        """Fetch and transform country investment data"""
        url = f"{self.base_url}/fund-chart/{slug}/investments-count-by-country"
        params = {
            "groupBy": "month",
            "startDate": start_date,
            "endDate": end_date,
            "slug": slug
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in country investments response")
                return {}

            return self._transform_country_investment_data(json_data)
        except Exception as e:
            print(f"Country Investments API Error: {str(e)}")
            return {}

    def _transform_country_investment_data(self, raw_data: dict) -> dict:
        """Transform country investment data with full structure"""
        transformed = {
            'countries': [],
            'totals': {
                'normal': raw_data.get('normalCount', 0),
                'lead': raw_data.get('leadCount', 0)
            }
        }

        for country_data in raw_data.get('data', []):
            country_entry = {
                'code': country_data.get('country', {}).get('code'),
                'name': country_data.get('country', {}).get('name'),
                'investments': {
                    'normal': country_data.get('normalCount', 0),
                    'lead': country_data.get('leadCount', 0),
                    'total': country_data.get('normalCount', 0) + country_data.get('leadCount', 0)
                },
                'categories': []
            }

            # Process categories if available
            for cat in country_data.get('categories', []):
                country_entry['categories'].append({
                    'name': cat.get('name'),
                    'count': cat.get('count', 0),
                    'percentage': round(float(cat.get('percent', 0)), 2)
                })

            transformed['countries'].append(country_entry)

        # Sort countries by total investments descending
        transformed['countries'].sort(
            key=lambda x: x['investments']['total'],
            reverse=True
        )

        return transformed



        # Add to the FundAPITester class
    def get_investments_by_month(self, slug: str, start_date: str, end_date: str):
        """Fetch monthly investment statistics with date filtering"""
        url = f"{self.base_url}/fund-chart/{slug}/investments-count-by-month"
        params = {
            "groupBy": "month",
            "startDate": start_date,
            "endDate": end_date,
            "slug": slug
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in investments response")
                return {}

            return self._transform_investment_data(json_data)
        except Exception as e:
            print(f"Investments API Error: {str(e)}")
            return {}

    def _transform_investment_data(self, raw_data: dict) -> dict:
        """Transform investment timeline data"""
        transformed = {
            'months': [],
            'totals': {
                'normal': raw_data.get('normalCount', 0),
                'lead': raw_data.get('leadCount', 0)
            }
        }

        for entry in raw_data.get('data', []):
            # Convert ISO date to "YYYY-MM" format
            date_str = entry.get('date', '')[:7]  # Gets "YYYY-MM" from ISO string

            transformed['months'].append({
                'period': date_str,
                'normal': entry.get('normalCount', 0),
                'lead': entry.get('leadCount', 0),
                'total': entry.get('normalCount', 0) + entry.get('leadCount', 0)
            })

        return transformed



        # Add to the FundAPITester class
    def get_news(self, slug: str, limit=10):
        """Fetch and transform complete news data"""
        url = f"{self.base_url}/news?lang=en&limit={limit}&fundsSlugs={slug}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()
            return self._transform_news_data(json_data.get('data', []))
        except Exception as e:
            print(f"News API Error: {str(e)}")
            return []

    def _transform_news_data(self, raw_news: list) -> list:
        """Transform all fields from the news API response"""
        transformed = []
        for item in raw_news:
            # Handle potential missing fields with .get()
            news_item = {
                # Core metadata
                'id': item.get('id'),
                'url_id': item.get('urlId'),
                'date': self._format_timestamp(item.get('date')),
                'title': item.get('title'),
                'description': item.get('description'),
                'url': item.get('url'),

                # Media
                'image': item.get('imageUrl'),
                'fallback_image': item.get('fallbackImageUrl'),

                # Content details
                'reading_time': self._format_reading_time(item.get('readingTimeMinutes')),
                'source': {
                    'name': item.get('source', {}).get('name'),
                    'lang': item.get('source', {}).get('lang')
                },

                # Relationships
                'coins': [
                    {
                        'key': coin.get('key'),
                        'symbol': coin.get('symbol'),
                        'name': coin.get('name')
                    } for coin in item.get('relatedCoins', [])
                ],
                'tags': [
                    {
                        'id': tag.get('id'),
                        'key': tag.get('key'),
                        'name': tag.get('name')
                    } for tag in item.get('tags', [])
                ],

                # Flags
                'is_ad': item.get('isAdvertisement', False)
            }
            transformed.append(news_item)
        return transformed

    def _format_timestamp(self, ts: int) -> str:
        """Convert millisecond timestamp to readable date"""
        if not ts: return "Date N/A"
        try:
            return datetime.fromtimestamp(ts/1000).strftime("%b %d, %Y %H:%M")
        except:
            return "Invalid Date"

    def _format_reading_time(self, minutes: [str,float,int]) -> str:
        """Safely format reading time"""
        try:
            return f"{float(minutes):.1f} min"
        except (TypeError, ValueError):
            return "N/A"


        # Add to the FundAPITester class
    def get_co_funds(self, fund_id: int):
        """Fetch and transform co-funding partners data"""
        url = f"{self.base_url}/coin-funds/{fund_id}/co-funds"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in co-funds response")
                return []

            return self._transform_co_funds_data(json_data['data'])
        except Exception as e:
            print(f"Co-Funds API Error: {str(e)}")
            return []

    def _transform_co_funds_data(self, raw_co_funds: list) -> list:
        """Transform co-funding partners data"""
        transformed = []
        for fund in raw_co_funds:
            transformed_fund = {
                'id': fund.get('fundId'),
                'slug': fund.get('slug'),
                'name': fund.get('name'),
                'logo': fund.get('logo'),
                'tier': fund.get('tier'),
                'type': fund.get('fundType'),
                'location': fund.get('location'),
                'stats': {
                    'co_investments': fund.get('coInvestmentsCount', 0),
                    'lead_investments': fund.get('leadCount', 0)
                },
                'investment_types': [
                    {'type': k, 'count': v}
                    for k, v in fund.get('types', {}).items()
                ],
                'categories': [
                    {'category': k, 'count': v}
                    for k, v in fund.get('categories', {}).items()
                ],
                'tags': fund.get('tags', []),
                'crowdsales': fund.get('crowdsalesTypes', []),
                'countries': fund.get('countries', []),
                'raise_ranges': fund.get('raises', [])
            }
            transformed.append(transformed_fund)
        return sorted(transformed, key=lambda x: x['stats']['co_investments'], reverse=True)


        # Add to the FundAPITester class
    def get_avg_round_raise(self, slug: str):
      """Fetch and transform average funding round data"""
      url = f"{self.base_url}/coin-funds/avg-round-raise/{slug}"
      try:
          response = requests.get(url, headers=self.headers, timeout=self.timeout)
          response.raise_for_status()
          json_data = response.json()

          if 'data' not in json_data:
              print("❌ Missing data in average round response")
              return []

          return self._transform_round_data(json_data['data'])  # Ensure key exists
      except Exception as e:
          print(f"Average Round API Error: {str(e)}")
          return []

    # In the FundAPITester class
    def _format_range(self, min_val, max_val):
        """Format funding range in human-readable format"""
        def to_millions(value):
            return f"${round(value/1_000_000)}M" if value else ""  # Corrected syntax

        if min_val == 0 and max_val == 1_000_000:
            return "Under $1M"
        if max_val is None:
            return f"{to_millions(min_val)}+"
        return f"{to_millions(min_val)} - {to_millions(max_val)}"

    def _transform_round_data(self, raw_rounds: list) -> list:
      """Transform and format round raise data"""
      transformed = []
      for r in raw_rounds:
          min_val = r.get('raiseFrom', 0)
          max_val = r.get('raiseTo')
          transformed.append({
              'range': self._format_range(min_val, max_val),
              'percentage': float(r.get('percent', 0)),
              'min': min_val,
              'max': max_val
          })
      # Fix: Use square brackets for dict access
      return sorted(transformed, key=lambda x: x['min'])  # Corrected line


        # Add to the FundAPITester class
    def get_recent_funding(self, slug: str):
        """Fetch and transform recent funding rounds"""
        url = f"{self.base_url}/coin-funds/recent-funding-rounds/{slug}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in funding rounds response")
                return []

            return self._transform_funding_data(json_data['data'])
        except Exception as e:
            print(f"Funding Rounds API Error: {str(e)}")
            return []

    def _transform_funding_data(self, raw_funding: list) -> list:
        """Transform and format funding round data"""
        transformed = []
        for round in raw_funding:
            # Parse and format date
            raw_date = round.get('date')
            formatted_date = None
            try:
                date_obj = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%b %d, %Y")
            except:
                formatted_date = "Date N/A"

            transformed.append({
                'date': formatted_date,
                'company': {
                    'name': round.get('coinName'),
                    'key': round.get('coinKey'),
                    'logo': round.get('coinLogo')
                },
                'amount': round.get('raise', 0),
                'stage': round.get('stage', '').title().replace('_', ' '),
                'category': {
                    'name': round.get('categoryName'),
                    'slug': round.get('categorySlug')
                },
                'formatted_amount': f"${round.get('raise', 0):,}",
                'timeline': f"{formatted_date} • {round.get('stage', '').title()}"
            })

        # Sort by date descending
        return sorted(transformed,
                    key=lambda x: x['date'],
                    reverse=True)


    def get_preferred_stages(self, slug: str):
        """Fetch and transform investment stage preferences"""
        url = f"{self.base_url}/coin-funds/preferred-stage/{slug}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in preferred stage response")
                return []

            return self._transform_stage_data(json_data['data'])
        except Exception as e:
            print(f"Preferred Stage API Error: {str(e)}")
            return []

    def _transform_stage_data(self, raw_stages: list) -> list:
        """Transform and sort stage preference data"""
        transformed = [
            {
                'stage': stage.get('type', 'Unknown').title(),
                'percentage': float(stage.get('percent', 0))
            }
            for stage in raw_stages
        ]
        return sorted(transformed, key=lambda x: x['percentage'], reverse=True)



    # Add to the FundAPITester class
    def get_funding_countries(self, slug: str):
        """Fetch and transform funding countries data"""
        url = f"{self.base_url}/coin-funds/main-funding-countries/{slug}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in funding countries response")
                return []

            return self._transform_countries_data(json_data['data'])
        except Exception as e:
            print(f"Funding Countries API Error: {str(e)}")
            return []

    def _transform_countries_data(self, raw_countries: list) -> list:
        """Transform country funding data"""
        return sorted([
            {
                'country': country.get('country'),
                'investments': country.get('count', 0)
            }
            for country in raw_countries
        ], key=lambda x: x['investments'], reverse=True)

    # Add to the FundAPITester class
    def get_social_activity(self, fund_id: int):
        """Fetch and transform social activity data"""
        url = f"{self.base_url}/coin-funds/{fund_id}/social-activity"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in social activity response")
                return None

            return self._transform_social_data(json_data['data'])
        except Exception as e:
            print(f"Social Activity API Error: {str(e)}")
            return None

    def _transform_social_data(self, raw_social: dict) -> dict:
        """Transform social activity data"""
        return {
            'profile_url': raw_social.get('link_url'),
            'twitter': {
                'username': raw_social.get('twitter_username'),
                'score': raw_social.get('twitter_score'),
                'followers': raw_social.get('followers_count'),
                'latest_followings': raw_social.get('latest_followings', [])
            }
        }

        # Add to the FundAPITester class
    def get_team_data(self, slug: str):
        """Fetch and transform team data"""
        url = f"{self.base_url}/team/by-fund-key/{slug}"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in team API response")
                return []

            return self._transform_team_data(json_data['data'])
        except Exception as e:
            print(f"Team API Error: {str(e)}")
            return []

    def _transform_team_data(self, raw_team: list) -> list:
        """Transform team member data"""
        return [
            {
                'name': member.get('name'),
                'photo': member.get('logo'),
                'roles': member.get('jobs', []),
                'links': {
                    link['type']: link['value']
                    for link in member.get('links', [])
                    if 'type' in link and 'value' in link
                }
            }
            for member in raw_team
        ]


    def get_fund_data(self, slug: str):
        """Fetch and transform complete fund data"""
        url = f"{self.base_url}/coin-funds/by-slug/{slug}/?locale=en"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            json_data = response.json()

            if 'data' not in json_data:
                print("❌ Missing data in API response")
                return None

            return self._transform_complete_data(json_data['data'])
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def _transform_complete_data(self, raw_data: dict) -> dict:
        """Transform all fields from the API response"""
        return {
            # Basic Info
            'basic': {
                'id': raw_data.get('id'),
                'slug': raw_data.get('slug'),
                'name': raw_data.get('name'),
                'tier': raw_data.get('tier'),
                'category': raw_data.get('category', {}),
                'country': raw_data.get('country'),
                'tabs': raw_data.get('tabs', [])
            },

            # Performance Metrics
            'performance': {
                'investments': raw_data.get('investments'),
                'roi': raw_data.get('roi'),
                'categories_distribution': [
                    {
                        'name': cat.get('name'),
                        'count': cat.get('count'),
                        'percentage': cat.get('percentage')
                    } for cat in raw_data.get('categoriesDistribution', [])
                ]
            },

            # Content
            'content': {
                'short_description': raw_data.get('shortDescription'),
                'description': html.unescape(raw_data.get('description', ''))
            },

            # Media Assets
            'media': {
                **raw_data.get('images', {}),
                'logos': {
                    'x60': raw_data.get('images', {}).get('x60'),
                    'x150': raw_data.get('images', {}).get('x150'),
                    'icon': raw_data.get('images', {}).get('icon'),
                    'native': raw_data.get('images', {}).get('native')
                }
            },

            # Investments
            'investments': {
                'top': [
                    {
                        'name': inv.get('name'),
                        'key': inv.get('key'),
                        'logo': inv.get('logo'),
                        'raise': inv.get('raise'),
                        'hidden': inv.get('isHidden')
                    } for inv in raw_data.get('topInvestments', [])
                ]
            },

            # Social Links
            'links': {
                link['type']: link['value']
                for link in raw_data.get('links', [])
                if 'type' in link and 'value' in link
            }
        }


############################End of the FundAPITester class#############################