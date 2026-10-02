import argparse

from commands.add import add
from commands.branch import branch
from commands.commit import commit
from commands.checkout import checkout
from commands.init import init
from commands.log import log
from commands.status import status


def main():
	parser = argparse.ArgumentParser(prog="mygit")
	subparsers = parser.add_subparsers(dest="command")

	init_parser = subparsers.add_parser("init")
	init_parser.set_defaults(handler=init)

	add_parser = subparsers.add_parser("add")
	add_parser.add_argument("files", nargs="+")

	branch_parser = subparsers.add_parser("branch")
	branch_parser.add_argument("name", nargs="?")

	checkout_parser = subparsers.add_parser("checkout")
	checkout_parser.add_argument("name")

	commit_parser = subparsers.add_parser("commit")
	commit_parser.add_argument("-m", "--message", required=True)

	subparsers.add_parser("log")
	subparsers.add_parser("status")

	args = parser.parse_args()

	if args.command == "add":
		add(args.files)
	elif args.command == "branch":
		branch(args.name)
	elif args.command == "checkout":
		checkout(args.name)
	elif args.command == "commit":
		commit(args.message)
	elif args.command == "log":
		log()
	elif args.command == "status":
		status()
	elif args.command == "init":
		init()
	else:
		parser.print_help()


if __name__ == "__main__":
	main()
