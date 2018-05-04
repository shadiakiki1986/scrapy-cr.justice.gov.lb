import betamax
import requests

CASSETTE_LIBRARY_DIR = 'tests/fixtures/cassettes/'


def main():
    session = requests.Session()
    recorder = betamax.Betamax(
        session, cassette_library_dir=CASSETTE_LIBRARY_DIR
    )

    with recorder.use_cassette('after_search'):
        session.get('https://httpbin.org/get')


if __name__ == '__main__':
    main()
