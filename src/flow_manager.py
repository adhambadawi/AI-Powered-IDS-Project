from scapy.all import IP, TCP, UDP
from datetime import datetime
from data_models.flow import Flow
from data_models.flow_packet import FlowPacket, Direction
from signal_manager import SignalManager

class FlowManager:
    def __init__(self, signal_manager: SignalManager, ipv4_address: str):
        self._flows = {}
        self._signal_manager = signal_manager
        self._ipv4_address = ipv4_address

    def _process_packet(self, packet) -> FlowPacket:
        """Convert raw packet to instance of flow packet data class

        Args:
            packet (_type_): Raw packet from scapy

        Returns: FlowPacket
        """
        if IP in packet:
            protocol = "TCP" if TCP in packet else "UDP"
            source_ip = packet[IP].src
            destination_ip = packet[IP].dst
            source_port = packet.sport
            destination_port = packet.dport
            if destination_ip == self._ipv4_address:
                direction = Direction.FORWARD
            else:
                direction = Direction.BACKWARD
            
            return FlowPacket(
                protocol,
                direction,
                source_ip,
                destination_ip,
                source_port,
                destination_port,
                datetime.now().microsecond,
                len(packet),
                self._get_segment_size(packet)
            )

        return None
    
    def _get_segment_size(self, packet):
        """Get the segment size of a packet

        Args:
            packet (_type_): Raw packet

        Returns:
            _type_: Segment size
        """
        total_size = len(packet)
        
        header_size = packet[0].ihl * 4
        if TCP in packet:
            header_size += packet[TCP].dataofs * 4
        elif UDP in packet:
            header_size += 8
        
        segment_size = total_size - header_size
        return segment_size
    
    def _get_flow_key(self, flow_packet: FlowPacket) -> tuple:
        """Get the flow key from a packet in the flow

        Args:
            flow_packet (FlowPacket): Flow packet

        Returns:
            tuple: Tuple representing flow key
        """
        if flow_packet.direction == Direction.FORWARD:
            return (flow_packet.protocol, flow_packet.source_ip, flow_packet.destination_ip, flow_packet.source_port, flow_packet.destination_port)
        else:
            return (flow_packet.protocol, flow_packet.destination_ip, flow_packet.source_ip, flow_packet.destination_port, flow_packet.source_port)

    def packet_callback(self, packet):
        """Callback function to process each packet."""
        if TCP not in packet and UDP not in packet:
            return
        
        flow_packet = self._process_packet(packet)
        key = self._get_flow_key(flow_packet)
        if key:
            if key not in self._flows:
                self._flows[key] = Flow(
                    [],
                    key[1],
                    key[2],
                    key[3],
                    key[4],
                    flow_packet.arrival_time,
                    flow_packet.arrival_time
                )
            
            self._flows[key].packets.append(flow_packet)
            self._flows[key].last_packet_timestamp = flow_packet.arrival_time
            self._signal_manager.process_input(self._flows[key])