// #########################################################################
// # Copyright/License Notice (Modified BSD License)                       #
// #########################################################################
// #########################################################################
// # Copyright (c) 2008, Daniel Knaggs                                     #
// # All rights reserved.                                                  #
// #                                                                       #
// # Redistribution and use in source and binary forms, with or without    #
// # modification, are permitted provided that the following conditions    #
// # are met: -                                                            #
// #                                                                       #
// #   * Redistributions of source code must retain the above copyright    #
// #     notice, this list of conditions and the following disclaimer.     #
// #                                                                       #
// #   * Redistributions in binary form must reproduce the above copyright #
// #     notice, this list of conditions and the following disclaimer in   #
// #     the documentation and/or other materials provided with the        #
// #     distribution.                                                     #
// #                                                                       #
// #   * Neither the name of the author nor the names of its contributors  #
// #     may be used to endorse or promote products derived from this      #
// #     software without specific prior written permission.               #
// #                                                                       #
// #   * This Software is not to be used for safety purposes.              #
// #                                                                       #
// #   * You agree and abide the Disclaimer for your Boltek StormTracker.  #
// #                                                                       #
// # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
// # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
// # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
// # A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
// # OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
// # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
// # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
// # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
// # THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
// # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
// # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
// #########################################################################

// Includes
#include <stdio.h>
#include <unistd.h>


// Socket
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <string.h>


// StormTracker
#include "stormpci.h"


// Constants
#define MAX_CONNECTIONS 1
#define WAIT_AMOUNT 1000
#define VERSION "0.1.0"

void sendSentence(int sock, char *sentence)
{
	int len = strlen(sentence);

	if (send(sock, sentence, len, 0) != len)
	{
		printf("Warning: Mismatch in number of bytes sent.\n");
	}
}

int main(int argc, char *argv[])
{
	printf("Welcome to the StormTracker to StormForce driver v%s\n", VERSION);
	printf("=======================================================\n");
	printf("\n");
	printf("#########################################################################\n");
	printf("# Copyright/License Notice (Modified BSD License)                       #\n");
	printf("#########################################################################\n");
	printf("#########################################################################\n");
	printf("# Copyright (c) 2008, Daniel Knaggs                                     #\n");
	printf("# All rights reserved.                                                  #\n");
	printf("#                                                                       #\n");
	printf("# Redistribution and use in source and binary forms, with or without    #\n");
	printf("# modification, are permitted provided that the following conditions    #\n");
	printf("# are met: -                                                            #\n");
	printf("#                                                                       #\n");
	printf("#   * Redistributions of source code must retain the above copyright    #\n");
	printf("#     notice, this list of conditions and the following disclaimer.     #\n");
	printf("#                                                                       #\n");
	printf("#   * Redistributions in binary form must reproduce the above copyright #\n");
	printf("#     notice, this list of conditions and the following disclaimer in   #\n");
	printf("#     the documentation and/or other materials provided with the        #\n");
	printf("#     distribution.                                                     #\n");
	printf("#                                                                       #\n");
	printf("#   * Neither the name of the author nor the names of its contributors  #\n");
	printf("#     may be used to endorse or promote products derived from this      #\n");
	printf("#     software without specific prior written permission.               #\n");
	printf("#                                                                       #\n");
	printf("#   * This Software is not to be used for safety purposes.              #\n");
	printf("#                                                                       #\n");
	printf("#   * You agree and abide the Disclaimer for your Boltek StormTracker.  #\n");
	printf("#                                                                       #\n");
	printf("# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #\n");
	printf("# \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #\n");
	printf("# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #\n");
	printf("# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #\n");
	printf("# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #\n");
	printf("# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #\n");
	printf("# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #\n");
	printf("# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #\n");
	printf("# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #\n");
	printf("# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #\n");
	printf("# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #\n");
	printf("#########################################################################\n");
	printf("\n");
	
	if (argc != 3)
	{
		printf("Warning: This program only takes 2 arguments like this: ./st2sf 0 23456\n");
		printf("         The first argument is the squelch level and the second argument is the network port to listen on.\n");
		return 0;
	}
	
	printf("Information: Preparing to connect to StormTracker...\n");
	
	
	// StormTracker
	int stormtracker_ready;
	
	StormProcess_tPACKEDDATA packed_info;
	StormProcess_tBOARDDATA unpacked_info;
	StormProcess_tSTRIKE strike;
	
	time_t currenttime;
	
	
	// Socket
	int serversock, clientsock;
	
	struct sockaddr_in stserver, stclient;
	
	
	// First connect to the StormTracker
	printf("Information: Attempting to connect to StormTracker...\n");
	
	if (StormPCI_OpenPciCard())
	{
		printf("Information: Connected to the StormTracker, setting squelch level to %d...\n", atoi(argv[1]));
		StormPCI_SetSquelch(atoi(argv[1]));
		
		
		printf("Information: Waiting for StormForce to connect on port TCP/%d...\n", atoi(argv[2]));
		
		// Now setup the inbound connection so StormForce can connect to it
		if ((serversock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
		{
			printf("Warning: Failed to create socket.\n");
			return 1;
		}
		
		memset(&stserver, 0, sizeof(stserver));
		
		stserver.sin_family = AF_INET;
		stserver.sin_addr.s_addr = htonl(INADDR_ANY);
		stserver.sin_port = htons(atoi(argv[2]));
		
		// Bind to interface
		if (bind(serversock, (struct sockaddr *) &stserver, sizeof(stserver)) < 0)
		{
			printf("Warning: Failed to bind the server socket.\n");
			return 1;
		}
		
		// Listen on the server socket
		if (listen(serversock, MAX_CONNECTIONS) < 0)
		{
			printf("Warning: Failed to listen on server socket.\n");
			return 1;
		}
		
		
		// Don't poll the StormTracker unless we've got a connection
		unsigned int clientlen = sizeof(stclient);
		
		// Wait for client connection
		if ((clientsock = accept(serversock, (struct sockaddr *) &stclient, &clientlen)) < 0)
		{
			printf("Warning: Failed to accept client connection.\n");
			return 1;
		}
		
		printf("Information: StormForce has connected from %s.\n", inet_ntoa(stclient.sin_addr));
		printf("Information: Polling StormTracker for strikes...\n");
		
		// Start polling the StormTracker...
		int statusCount = 0;
		
		while (1)
		{
			stormtracker_ready = StormPCI_StrikeReady();
			
			// Ensure we have something to parse
			if (stormtracker_ready)
			{
				StormPCI_GetBoardData(&packed_info);
				StormPCI_RestartBoard();
				
				StormProcess_UnpackCaptureData(&packed_info, &unpacked_info);
				strike = StormProcess_SSProcessCapture(&unpacked_info);
				
				// Is the strike valid?
				if (strike.valid)
				{
					// Yes it is, now we can get the details of it
					char sentence[255] = "$WINLI,";
					char tmp[100] = "";
					
					// Must be an easier way to do this?
					sprintf(tmp, "%3.3f", strike.distance_averaged);
					strcat(sentence, tmp);
					strcat(sentence, ",");
					
					sprintf(tmp, "%3.3f", strike.distance);
					strcat(sentence, tmp);
					strcat(sentence, ",");
					
					sprintf(tmp, "%3.1f", strike.direction);
					strcat(sentence, tmp);
					strcat(sentence, ",");
					
					strcat(sentence, "CG");
					strcat(sentence, ",");
					strcat(sentence, "-");
					strcat(sentence, "*FF\n");
					
					sendSentence(clientsock, sentence);
				}
				else
				{
					// No it isn't, must be noise
					sendSentence(clientsock, "$WINLN*FF\n");
				}
			}
			
			// Shall we send a status?
			if (statusCount == 1000)
			{
				// One second has elapsed so send a status message
				sendSentence(clientsock, "$WINST*FF\n");
				statusCount = 0;
			}
			else
			{
				statusCount += 1;
				
				// Just in-case...
				if (statusCount > 1000)
					statusCount = 1000;
			}
			
			// Wait one millisecond other we'll get 100% CPU usage
			usleep(WAIT_AMOUNT); // usleep() - amount to wait in microseconds (uS)
		}

		printf("Information: Polling terminated, shutting down...\n");
		
		StormPCI_ClosePciCard();
		return 0;
	}
	else
	{
		printf("Error: Unable to access the Boltek StormTracker.\n");
		return 1;
	}
	
	printf("Warning: Unexpected program termination.\n");
	return 1;
}
