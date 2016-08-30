#!/usr/bin/env python

'''
CoCrawler web crawler, main program
'''
import sys

import argparse
import asyncio
import logging

import config
import cocrawler
import stats

ARGS = argparse.ArgumentParser(description='CoCrawler web crawler')
ARGS.add_argument('--config', action='append')
ARGS.add_argument('--configfile', action='store')
ARGS.add_argument('--no-confighome', action='store_true')
ARGS.add_argument('--no-test', action='store_true')
ARGS.add_argument('--printdefault', action='store_true')
ARGS.add_argument('--load', action='store')

def main():
    '''
    Main program: parse args, read config, set up event loop, run the crawler.
    '''

    args = ARGS.parse_args()

    if args.printdefault:
        config.print_default()
        sys.exit(1)

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]

    # need to set up logging to log while reading the conf file to find out the logging level
    # XXX maybe get this from the command-line?
    logging.basicConfig(level=levels[2])
    conf = config.config(args.configfile, args.config, confighome=not args.no_confighome)

    if args.no_test and conf['Testing'].get('StatsEQ') is not None:
        del conf['Testing']['StatsEQ']
    kwargs = {}
    if args.load:
        kwargs['load'] = args.load

    log_level = conf['Logging']['LoggingLevel']
    # XXX can't call this twice :/
    logging.basicConfig(level=levels[min(int(log_level), len(levels)-1)])

    loop = asyncio.get_event_loop()
    crawler = cocrawler.Crawler(loop, conf, **kwargs)

    try:
        loop.run_until_complete(crawler.crawl())
    except KeyboardInterrupt: # pragma: no cover
        sys.stderr.flush()
        print('\nInterrupt\n')
#    except Exception as e: # XXX this doesn't seem to surface anything
#        print('exception consumed: {}'.format(e))
    finally:
        crawler.close()
        # apparently this is needed for full aiohttp cleanup
        loop.stop()
        loop.run_forever()
        loop.close()

if __name__ == '__main__':
    main()
    exit(stats.exitstatus)
