import logging
import sys

from dotenv import load_dotenv

from src.model import initialize_llm, load_llm_config
from src.ui import ChatUI, get_chat_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s:%(lineno)d [%(levelname)s]  - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Load environment variables")
load_dotenv(override=True)


def main():
    try:
        # Load configuration with environment variable validation
        logger.info("Loading LLM configuration...")
        config = load_llm_config()

        # Initialize the LLM with the configuration
        logger.info("Initializing LLM...")
        initialize_llm(config=config, eager_loading=True)

        # Get chat manager
        chat_manager = get_chat_manager()

        # Launch the chat interface
        logger.info("Launching chat interface...")
        ChatUI.launch_chat_interface(chat_manager)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
