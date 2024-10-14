import rollbar

def main():
    rollbar.init('post_server_item_token', 'testenv')  # токен доступа, среда
    rollbar.report_message('Test message from backend', 'info')

if __name__ == "__main__":
    main()