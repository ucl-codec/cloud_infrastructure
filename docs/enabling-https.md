# Enabling https encryption with PassianFL

Communication to PassianFL already occurs through an encrypted VPN connection.
For additional security, you can also enforce TLS-encrypted https on the PassianFL web services.

In order to enable https, you must own one or more public-facing web domains for which you can modify NS records.
Although the actual communication with PassianFL is over private networks, a public domain is still 
necessary in order for AWS to generate and approve the required encryption certificates.

---

## How to set up your DNS records
These steps must be followed before you deploy PassianFL with https enabled

1. Register a domain, e.g. `example.com` from your chosen provider
2. Create a public hosted zone in AWS 
   - In the AWS console, go to `Route 53` > `Hosted Zones`, `Create hosted zone`
   - Enter the domain name matching the domain you registered above, e.g. `example.com`
   - Choose `Public hosted zone` and click `Create hosted zone`
   - Next to `Hosted zone details`, click the arrow to expand. Note down the four `Name servers` on the right
3. Update the NS records on your registrar 
   - Go to your registrar's website and view the DNS records for your domain
   - Modify the NS records for your domain. Set them to the four name servers you wrote down earlier
  
    _Important: do not modify the DNS records on the AWS hosted zone. Modify the NS records on your registar's website to match the records shown on AWS_ 

---

## Notes
- The domain `example.com` should be added to your configuration file as the `parent_domain` for the network and/or nodes
- Deployment will fail if you enable https but haven't completed the DNS steps above.
- You can use the same domain `example.com` for the network and one or more nodes, or you can use separate domains for each network.
- PassianFL will create subdomains under the parent domain. For example, if your parent domain is `example.com`, PassianFL will
create subdomains `researcher.example.com` for the researcher node, `nodea.example.com` for the local node "nodea", and so on.
- PassianFL wil automatically create AWS certificates for each web server. In order to approve the certificate, AWS adds a CNAME
record to the public hosted zone. If you have not correctly configured your NS records as described above, the certificate validation will fail during deployment.
- The public hosted zones are only used for certificate validation. When using PassianFL, communication is over private networks. 

---

## Alternative: use of a private CA

Alternatively, you can enable https encryption without using a public domain, by creating a private 
certificate authority and use this to manage certificates for the web services. In this situation, 
you must add your private CA root certificates to all the clients who will be connecting to your 
PassianFL system, otherwise your browsers may display security errors or block the connections.
