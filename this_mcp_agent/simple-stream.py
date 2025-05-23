import asyncio
import os
import time
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from kasa import Discover, KasaException    
from lightTools import turn_on_light, turn_off_light, set_light_brightness, set_light_hsv, get_light_state
from calenderTools import list_calendar_events, create_calendar_event, delete_calendar_event

load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

class AsyncSlackMonitor:
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.running = False
        self.session_service = InMemorySessionService()
        self.session = None
        self.runner = None
        self.agent = None
        
    async def setup_agent_with_mcp(self):
        """Set up agent with properly managed MCP connections."""
        print("Setting up MCP connections...")
        
        # Create MCP toolsets with proper async handling
        maps_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y", "@modelcontextprotocol/server-google-maps"],
                env={"GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY")}
            ),
        )

        airbnb_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            ),
        )

        slack_toolset = MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y", "@modelcontextprotocol/server-slack"],
                env={
                    "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
                    "SLACK_TEAM_ID": "<team_id>",
                    "SLACK_CHANNEL_IDS": "<channel_id>",
                }
            ),
        )
        
        # Create agent with MCP tools and custom functions
        self.agent = LlmAgent(
            model='gemini-2.5-flash-preview-05-20',
            name='slack_travel_smart_home_assistant',
            instruction="""
            You are a comprehensive assistant that monitors and responds in Slack channel C08TKVAS5TP.
            You can help with travel planning, smart home control, and general questions.
            When a user asks for general information, use the search_toolset tool to get realtime information.
            
            When prompted to check Slack:
            1. Read recent messages from the channel using Slack tools
            2. Look for messages that need assistance with:
               - Travel planning (accommodation, directions, etc.)
               - Smart home control (turning lights on/off)
               - General questions directed at you
            
            3. ALWAYS send a status update to the Slack channel using the Slack tools, either:
               - If you find relevant messages: respond helpfully using appropriate tools AND send your response to Slack
               - If no new messages need response: send a brief status update like "✅ I'm ready! No new requests at [timestamp]"
            
            For responses, use:
               - Airbnb tools for accommodation searches  
               - Maps tools for directions and location info
               - Light control functions (turn_on_light, turn_off_light) for smart home requests
               - Slack tools to ALWAYS send your final response/status back to the channel
            
            For light control:
            - Use turn_on_light() when users want to turn lights on
            - Use turn_off_light() when users want to turn lights off
            - Use get_light_state() to check the current state of the lights
            - Use set_light_hsv() to set the color of the lights
            - Use set_light_brightness() to set the brightness of the lights
            - The functions control lights at two locations automatically
            
            IMPORTANT: Always use Slack tools to send a message to the channel, even if it's just a status update.
            """,
            tools=[
                slack_toolset, 
                airbnb_toolset, 
                maps_toolset,
                turn_on_light,   
                turn_off_light,
                get_light_state,
                set_light_hsv,
                set_light_brightness,
                list_calendar_events,
                create_calendar_event,
                delete_calendar_event,
            ],
        )
        
        # Create session and runner
        self.session = await self.session_service.create_session(
            app_name="slack_monitor_app",
            user_id="slack_bot",
            session_id="monitoring_session"
        )
        
        self.runner = Runner(
            app_name="slack_monitor_app",
            agent=self.agent,
            session_service=self.session_service,
        )
        
        print("Agent and MCP connections set up successfully!")

    async def check_slack_and_respond(self):
        """Send a prompt to check Slack and respond to travel or smart home requests."""
        try:
            current_time = time.strftime('%H:%M:%S')
            prompt = f"Check Slack channel <channel_id> for any new messages and fulfill any requests. ALWAYS send a message to the Slack channel with either your response to requests or a status update if no requests found. Current time: {current_time}"
            content = types.Content(role='user', parts=[types.Part(text=prompt)])
            
            print(f"[{current_time}] Checking Slack for new messages...")
            
            # Use async runner
            events_async = self.runner.run_async(
                session_id=self.session.id,
                user_id=self.session.user_id,
                new_message=content
            )
            
            # Collect all responses
            all_responses = []
            async for event in events_async:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    response = event.content.parts[0].text
                    if response:
                        all_responses.append(response)
                        print(f"Agent action: {response[:150]}...")
            
            # If we collected responses, log the summary
            if all_responses:
                total_response = "\n".join(all_responses)
                print(f"Total agent response length: {len(total_response)} characters")
                print("Agent successfully processed and should have sent message to Slack")
            else:
                print("No agent response received - this might indicate an issue")
                        
        except Exception as e:
            print(f"Error during Slack check: {e}")
            # Try to send an error message to Slack
            try:
                error_prompt = f"Send an error status message to Slack channel <channel_id>: 'Error during monitoring at {time.strftime('%H:%M:%S')}: {str(e)[:100]}'"
                error_content = types.Content(role='user', parts=[types.Part(text=error_prompt)])
                
                events_async = self.runner.run_async(
                    session_id=self.session.id,
                    user_id=self.session.user_id,
                    new_message=error_content
                )
                async for event in events_async:
                    pass  # Just execute to send the error message
            except:
                print("Failed to send error message to Slack")

    async def monitor_loop(self):
        """Main monitoring loop using asyncio."""
        print(f"Starting Slack monitoring (checking every {self.check_interval} seconds)")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                await self.check_slack_and_respond()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.running = False
        except Exception as e:
            print(f"Monitoring error: {e}")
            self.running = False

    async def start(self):
        """Start the monitoring service."""
        await self.setup_agent_with_mcp()
        self.running = True
        await self.monitor_loop()

# Simple function to run the monitor
async def run_slack_monitor(check_interval=30):
    monitor = AsyncSlackMonitor(check_interval=check_interval)
    await monitor.start()

# Main execution
if __name__ == "__main__":
    try:
        # Run the async monitor
        asyncio.run(run_slack_monitor(check_interval=30))
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Error: {e}")