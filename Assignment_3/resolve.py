"""
resolve.py: a recursive resolver built using dnspython
"""

import argparse

import time
import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype

FORMATS = (("CNAME", "{alias} is an alias for {name}"),
           ("A", "{name} has address {address}"),
           ("AAAA", "{name} has IPv6 address {address}"),
           ("MX", "{name} mail is handled by {preference} {exchange}"))

# current as of March 7 2021

ROOT_SERVERS = ("198.41.0.4",
                "199.9.14.201",
                "192.33.4.12",
                "199.7.91.13",
                "192.203.230.10",
                "192.5.5.241",
                "192.112.36.4",
                "198.97.190.53",
                "192.36.148.17",
                "192.58.128.30",
                "193.0.14.129",
                "199.7.83.42",
                "202.12.27.33")


def collect_results(name: str) -> dict:
    """
    This function parses final answers into the proper data structure that
    print_results requires. The main work is done within the `lookup` function.
    """

    full_response = {}
    target_name = dns.name.from_text(name)
    # lookup CNAME
    response = lookup(target_name, dns.rdatatype.CNAME, ROOT_SERVERS)
    cnames = []
    for answers in response.answer:
        for answer in answers:
            cnames.append({"name": answer, "alias": name})
    # lookup A
    response = lookup(target_name, dns.rdatatype.A, ROOT_SERVERS)
    print('(53) response:', response)
    arecords = []
    for answers in response.answer:
        a_name = answers.name
        for answer in answers:
            if answer.rdtype == 1:  # A record
                arecords.append({"name": a_name, "address": str(answer)})
    # lookup AAAA
    response = lookup(target_name, dns.rdatatype.AAAA, ROOT_SERVERS)
    aaaarecords = []
    for answers in response.answer:
        aaaa_name = answers.name
        for answer in answers:
            if answer.rdtype == 28:  # AAAA record
                aaaarecords.append({"name": aaaa_name, "address": str(answer)})
    # lookup MX
    response = lookup(target_name, dns.rdatatype.MX, ROOT_SERVERS)
    mxrecords = []
    for answers in response.answer:
        mx_name = answers.name
        for answer in answers:
            if answer.rdtype == 15:  # MX record
                mxrecords.append({"name": mx_name,
                                  "preference": answer.preference,
                                  "exchange": str(answer.exchange)})

    full_response["CNAME"] = cnames
    full_response["A"] = arecords
    full_response["AAAA"] = aaaarecords
    full_response["MX"] = mxrecords

    return full_response

def lookup(target_name: dns.name.Name,
           qtype: dns.rdata.Rdata, servers) -> dns.message.Message:
    """
    This function uses a recursive resolver to find the relevant answer to the
    query.

    TODO: replace this implementation with one which asks the root servers
    and recurses to find the proper answer.
    """
    print('(95) servers:', servers)

    CNAME = []
    A = []
    AAAA = []
    MX = []

    outbound_query = dns.message.make_query(target_name, qtype)
    response = None 
    #print('(104) outbound query', outbound_query)
    #print('(105) testing second wave:', dns.query.udp(outbound_query, '192.5.6.3', 3))
    for server in servers:
        try:
                response = dns.query.udp(outbound_query, server, 3)
                #print(t, 'second(s) has elapsed (111)')
                #print('(107) type(response)', type(response))
                break
            #print("(114) didn't work out")
            #return None 
        except:
            pass 

    #print('(120) response:', response)
    CNAME = []
    A = []
    AAAA = []
    MX = []

    grab_ip = lambda x: str(x)[str(x).find('[<')+2:str(x).find('>]')+1]
    remove_pre_A = lambda x: x[x.find('IN A ')+5:len(x)]
#    print('(125) additional:', remove_pre_A(str(response.additional[0])))
    if response:
        for obj in response.additional:
            if ' A ' in str(obj):
                #A.append(obj)
                A.append(remove_pre_A(str(obj)))
            elif ' AAAA ' in str(obj):
                #AAAA.append(obj)
                AAAA.append(grab_ip(obj))
            elif ' MX ' in str(obj):
                #MX.append(obj)
                MX.append(grab_ip(obj))
            elif ' CNAME ' in str(obj):
                #CNAME.append(obj)
                CNAME.append(grab_ip(obj))
    print('(139) A:', A)
    if  response.answer == []:
        #A = list(map(lambda x: x[x.find('A ')+2:len(x)-2], A))
        lookup(target_name, dns.rdatatype.A, A)
    else:
        return response



#    print('(114) answer:', response.answer)
#    types = set([obj.rdtype for obj in response.additional])
#    print(types)


#    res = {'CNAME': CNAME, 'A': A, 'AAAA': AAAA, 'MX':MX}
    #print('(148) response:', response)
    #return response


def print_results(results: dict) -> None:
    """
    take the results of a `lookup` and print them to the screen like the host
    program would.
    """
    print('(157) results:',results)
    for rtype, fmt_str in FORMATS:
        for result in results.get(rtype, []):
            print(fmt_str.format(**result))


def main():
    """
    if run from the command line, take args and call
    printresults(lookup(hostname))
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("name", nargs="+",
                                 help="DNS name(s) to look up")
    
    program_args = argument_parser.parse_args()
    
    for a_domain_name in program_args.name:
        print_results(collect_results(a_domain_name))

if __name__ == "__main__":
    main()
