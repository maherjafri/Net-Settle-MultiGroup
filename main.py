import argparse
import server
def main():
    p=argparse.ArgumentParser(description="Net-Settle multi-group expense manager")
    p.add_argument("--ui",action="store_true",help="launch the web UI")
    p.add_argument("--port",type=int,default=8000)
    p.add_argument("--no-browser",action="store_true")
    args=p.parse_args()
    server.run(port=args.port,open_browser=not args.no_browser)
if __name__=="__main__": main()
