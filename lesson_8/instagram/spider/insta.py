import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instagram.items import InstagramItem

class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = ""
    insta_pwd = ""
    insta_login_link = "https://www.instagram.com/accounts/login/ajax/"

    parse_users = ['depinjoy_','chernovasia']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers = [{'query_hash' : 'c76146de99bb02f6415203be841dd25a', 'section':'edge_followed_by'},
                 {'query_hash' : 'd04b0a864b4b54837c0d870b0e77e076', 'section':'edge_follow'}]


    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST', # post запрос
            callback=self.user_parse,# метод, который примет ответ post запроса
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-cSRFToken':csrf_token}
        )
    def user_parse(self, response:HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for self.user in self.parse_users:
                yield response.follow(
                    f'/{self.user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username':self.user}
                )
    def user_data_parse(self,response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'include_reel': 'true',
            'fetch_mutual': 'false',
            'first': 50
        }
        for self.itm in self.followers:
            follow_section = self.itm['section']
            follow_hash = self.itm['query_hash']
            url_list = f"{self.graphql_url}query_hash={follow_hash}&{urlencode(variables)}"

            if self.itm['section'] == 'edge_followed_by':
                method = self.edge_followed_by
            else:
                method = self.edge_follow

            yield response.follow(
                url_list,
                callback=method,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'follow_section': deepcopy(follow_section),
                           'follow_hash': deepcopy(follow_hash),
                           'variables': deepcopy(variables)}
            )


    def edge_followed_by(self, response:HtmlResponse,username,user_id,follow_section,follow_hash,variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables['after']=page_info.get('end_cursor')
            url_list = f'{self.graphql_url}query_hash={follow_hash}&{urlencode(variables)}'
            yield response.follow(
                url_list,
                callback=self.edge_followed_by,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'follow_section': deepcopy(follow_section),
                           'follow_hash': deepcopy(follow_hash),
                           'variables': deepcopy(variables)}
            )
        users = j_data.get('data').get('user').get('edge_followed_by' ).get('edges')
        for user in users:
            item = InstagramItem(
                user_id = user_id,
                username = username,
                follow_type = follow_section,
                follow_id = user['node']['id'],
                user_name = user['node']['username'],
                full_name = user['node']['full_name'],
                photo = user['node']['profile_pic_url']
            )
            yield item

    def edge_follow(self, response:HtmlResponse,username,user_id,follow_section,follow_hash,variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables['after']=page_info.get('end_cursor')
            url_list = f'{self.graphql_url}query_hash={follow_hash}&{urlencode(variables)}'
            yield response.follow(
                url_list,
                callback=self.edge_follow,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'follow_section': deepcopy(follow_section),
                           'follow_hash': deepcopy(follow_hash),
                           'variables': deepcopy(variables)}
            )

        users = j_data.get('data').get('user').get('edge_follow').get('edges')
        for user in users:
            item = InstagramItem(
                user_id = user_id,
                username=username,
                follow_type = follow_section,
                follow_id = user['node']['id'],
                user_name = user['node']['username'],
                full_name = user['node']['full_name'],
                photo = user['node']['profile_pic_url']
            )
            yield item

    #Токен для авторизации (поиск)
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"','')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        result = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text)
        matched = result.group()
        return json.loads(matched).get('id')
