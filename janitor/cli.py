
import argparse
import logging

from janitor import policy, commands


def _default_options(p):
    p.add_argument("-r", "--region", default="us-east-1",
                   help="AWS Region to target (Default: us-east-1)")
    p.add_argument("--profile", default=None,
                   help="AWS Account Config File Profile to utilize")
    p.add_argument("--assume", default=None, dest="assume_role",
                   help="Role to assume")
    p.add_argument("-c", "--config", required=True,
                   help="Policy Configuration File")
    p.add_argument("-p", "--policies", default=None,
                   help="Only execute named/matched policies")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Verbose Logging")
    p.add_argument("--debug", action="store_true",
                   help="Dev Debug")
    p.add_argument("-s", "--output-dir", required=True,
                   help="Directory or S3 URL For Policy Output")
    p.add_argument("-f", "--cache", default="~/.cache/cloud-janitor.cache")
    p.add_argument("--cache-period", default=60, type=int,
                   help="Cache validity in seconds (Default 60)")

    
def _dryrun_option(p):
    p.add_argument(
        "-d", "--dryrun", action="store_true",
        help="Don't change infrastructure but verify access.")

    
def setup_parser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()


    blame = subs.add_parser("blame")
    blame.set_defaults(command=commands.blame)
    _default_options(blame)
    blame.add_argument(
        '--days', type=int,
        help="Number of days of history to consider")
    blame.add_argument(
        '--ip', action='append',
        help="Server IP Address to look for")
    blame.add_argument(
        '--instance-id', action='append',
        help="Server Instance Id to look for")

    
    identify = subs.add_parser("identify")
    identify.set_defaults(command=commands.identify)
    _default_options(identify)

    run = subs.add_parser("run")
    run.set_defaults(command=commands.run)
    _default_options(run)
    _dryrun_option(run)
    run.add_argument("-m", "--metrics-enabled",
        default=False, action="store_true",
        help="Emit CloudWatch Metrics (default false)")    
    
    return parser


def main():
    parser = setup_parser()
    options = parser.parse_args()

    level = options.verbose and logging.DEBUG or logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s: %(name)s:%(levelname)s %(message)s")
    logging.getLogger('botocore').setLevel(logging.ERROR)
    logging.getLogger('placebo').setLevel(logging.INFO)    
    
    config = policy.load(options, options.config)
    try:
        options.command(options, config)
    except Exception, e:
        if not options.debug:
            raise
        import traceback, pdb, sys
        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])
        

    

if __name__ == '__main__':
    main()

    