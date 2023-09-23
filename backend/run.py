import argparse
import os

from dotenv import load_dotenv
import uvicorn


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    
     # 將 parser.add_argument 的部分，分成不同的 group
    # 原本的改為 app_mode
    app_mode = parser.add_argument_group(title="App Mode", description="Run the server in different modes.")
    app_mode.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    app_mode.add_argument("--test",action="store_true", help="Run the server in test mode.")
    app_mode.add_argument("--dev",action="store_true", help="Run the server in development mode.")

    # 新增 db_type
    db_type =  parser.add_argument_group(title="Database Type", description="Run the server in different database type.")
    db_type.add_argument("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")
    
    args = parser.parse_args()

    if args.prod:
        load_dotenv("setting/.env.prod")
    elif args.test:
        load_dotenv("setting/.env.test")
    else:
        load_dotenv("setting/.env.dev")

    # 新增 DB_TYPE
    os.environ["DB_TYPE"] = args.db
    print("DB_TYPE",os.getenv("DB_TYPE"))

    uvicorn.run("main:app", host="0.0.0.0" , port=int(os.getenv("PORT")) , reload=bool(os.getenv("RELOAD")) )
    