# HHLA - Pre-announcement of Truck Visits - User Manual Analysis

**Document Source:** [Provided Document]
**Effective Date:** 2.0 – 01.01.2023

## 1. Introduction (Section 1)

*   **1.1 Purpose:** Reliable pre-announcement via TR02 (version 14) key for efficient truck processing at Hamburg container terminals. Pre-announcement improves efficiency and planning for all involved. Manual provides information for users to pre-announce truck transport data and technical documentation for software/system providers integrating TR02.
*   **1.2 Structure of the user manual:** Chapter overview (Chapter 2 - basic TR02 process, Chapter 3 - transport cases, Chapter 4 - slot booking).

## 2. General (Section 2)

*   **2.1 Operation:** 4-step process:
    1.  Haulage company submits transport/container data with status request (TR02).
    2.  Terminal reviews, checks feasibility, reports status (TR02) with processing instructions.
    3.  Haulage company/driver books transport (delivery/collection).
    4.  Terminal allocates Pre-Announcement Number (PAN) for truck visit (driver needs PAN at terminal).

*   **Processing Codes:** Status information reported back via TR02 includes Processing Codes indicating transport feasibility:

    *   **Not executable (500–699):**
        *   **500–699:** Incorrect data must be corrected by the truck driver or the haulage company.

    *   **Waiting (300–499):**
        *   **300–499:** Transport cannot be carried out yet. Automatic notification if status changes.

    *   **Executable (100–299):**
        *   **100–299:** The terminal transmits a pre-announcement number (PAN) to the truck driver or the haulage company.

*   **2.2 Connection Options:**
    *   **Systems Houses and EDI:** Haulage companies/forwarders connect via software providers/systems houses or direct EDI. Further info: www.truckgate.de.
    *   **Web Application:** Free web app available for truck drivers (Trucker card required). Links: web.truckgate.de, mobile app.truckgate.de.

*   **2.3 The Three Golden Rules:**
    1.  **Rule 1 - PAN Essential:** Drivers must keep their pre-announcement number (PAN) handy at all times. Containers will only be handled using this number.
    2.  **Rule 2 - Mandatory Booking:** Hauliers must book all truck visits (deliveries and/or collections). This is the only way to optimise processes together with the terminal.
    3.  **Rule 3 - Data Accuracy:** Keep your pre-announcement data up to date, and add missing information as soon as it becomes available. You will receive the right feedback and benefit from faster processing at the terminal only if your data is correct.

## 3. Cases of Application (Section 3)

*   **3.1 Overview:** Mandatory pre-announcement for all except some special cases. MPC (Manual Pre-Check) required in some cases even with pre-announcement. Some cases require additional code in status request.

    *   **Table 2 Cases of application in TR02 and their specific features:**

        | Case of application          | Obligation | Code | MPC | Note                                                                                                                             |
        | ---------------------------- | ---------- | ---- | --- | -------------------------------------------------------------------------------------------------------------------------------- |
        | **Standard container**       |            |      |     |                                                                                                                                |
        | Delivery                     | •          |      |     | Applies to export and transfer                                                                                                  |
        | Collection                   | •          |      |     | Applies to import and transfer                                                                                                 |
        | Empty depot/depot incoming   | •          | (•)  |     | Containers with turn-in reference (CTB only) via MPC; in all other cases without MPC.                                        |
        | Empty depot/depot outgoing  | •          |      |     |                                                                                                                                |
        | **Special containers**       |            |      |     |                                                                                                                                |
        | Reefer                       | •          | •    | (•) | Collection of reefer containers at CTA without MPC; in all other cases via MPC. Code required for non-operating reefers.       |
        | OOG containers               | •          | •    | •   |                                                                                                                                |
        | Hazardous cargo              | •          | •    | •   |                                                                                                                                |
        | **Special cases**            |            |      |     |                                                                                                                                |
        | CUSTOMS – NCTS Transit (T1)  | •          | •    | (•) | Collections in transit procedure at CTA without MPC; in all other cases via MPC.                                              |
        | KLV rail (land–land transport) | •          |      |     |                                                                                                                                |
        | Inspection                   | •          |      |     |                                                                                                                                |
        | Packing facility (CTB)       | •          |      |     |                                                                                                                                |
        | Collection of export container | •          |      |     |                                                                                                                                |

*   **3.2 Standard Container:** Planned arrival time always needed for slot booking.

    *   **3.2.1 Delivery:**

        *   **STANDARD DELIVERY WITH BOOKING NUMBER:** Booking number usually required for standard export container deliveries.

            *   **Data Elements:**
                *   Load status: Whether the container is full or empty
                *   Container number: Prefix + 7-digit number, same as the number on the container
                *   ISO code: ISO code in accordance with UN ISO6346
                *   Gross mass: Gross mass of the container in kg
                *   Booking number: Ship booking number of the container operator, same as on transport documents

            *   **Status Codes:**
                *   **100 OK:** The pre-announcement is correct; all prerequisites for self-service terminal handling with the pre-announcement number (PAN) have been met.
                *   **617 Booking number ambiguous:** The booking number provided cannot be clearly allocated. The shipping company code must be provided.
                *   **619 Booking number unknown:** The terminal does not (yet) have any booking data under the booking number specified. Alternatively, shipping companies that are unable to participate in booking data exchange can use the ship and port of discharge for pre-announcement.

        *   **STANDARD DELIVERY WITHOUT BOOKING NUMBER:** Alternative for shipping companies not in booking data exchange.

            *   **Data Elements:**
                *   Load status: Whether the container is full or empty
                *   Container number: Prefix + 7-digit number, same as the number on the container
                *   ISO code: ISO code in accordance with UN ISO6346
                *   Gross mass: Gross mass of the container in kg
                *   Carrier code: Container operator according to the DAKOSY code list
                *   Ship number: Ship number according to the previously submitted TR02 ship report
                *   Port of discharge: Port of discharge for the export container

            *   **Status Codes:**
                *   **100 OK:** The pre-announcement is correct; all prerequisites for self-service terminal handling with the pre-announcement number (PAN) have been met.
                *   **616 Booking number required:** Pre-announcement must be made using the booking number for the shipping company according to the carrier code.
                *   **620 Carrier code unknown:** The terminal does not recognise the carrier code (shipping company) provided. This means: 1. The terminal uses a different code from the DAKOSY key list for the shipping company. 2. The shipping company is not at the terminal.
                *   **621 Ship number unknown:** The terminal system does not recognise the ship number provided.
                *   **622 Port of discharge prohibited:** 1. The ship does not call at the port of discharge on this trip. 2. The system does not recognise the port of departure.

    *   **3.2.2 Collection:**

        *   **STANDARD COLLECTION WITHOUT DECLARATION OF RESPONSIBILITY:** PIN release process generally used.

            *   **Data Elements:**
                *   Load status: Whether the container is full or empty
                *   Container number: Prefix + 7-digit number, same as the number on the container
                *   Release reference: Release or authentication reference. Authentication is generally completed using the PIN release process. Authentication can only be performed based on name in exceptional cases.

            *   **Status Codes:**
                *   **100 OK:** The pre-announcement is correct; all prerequisites for self-service terminal handling with the pre-announcement number (PAN) have been met.
                *   **201 Automatic authentication check not possible:** The pre-announcement is correct. This indicates that the shipping company does not use the PIN release process. The pre-announcement is processed in the manual pre-check (MPC) following submission of the documents (authentication).
                *   **310 Container not yet in stock:** The terminal system recognises the container but it is not yet physically at the terminal.
                *   **550 Statutory prerequisites not met:** The container cannot be released for legal reasons (e.g. customs, veterinary office, water police). See 3.4.3 for collection in connection with inspection.
                *   **551 In custody:** The container cannot be released because the terminal is being held in custody by customs. See 3.4.1 for collections under the NCTS transit procedure.
                *   **601 No or unknown release:** The terminal does not have a release for the container.
                *   **602 Wrong release or authentication reference:** The release reference/PIN does not match the information provided by the shipping company.
                *   **611 Container currently unknown:** The terminal does not recognise the container, nor is it expected.
                *   **660 Container transport already scheduled:** A pre-announcement already exists for the container or the container has been assigned to another carrier.
                *   **670 Container blocked by terminal:** The container has not been released by the terminal.

        *   **STANDARD COLLECTION WITH QUAY ACCOUNT NUMBER (DECLARATION OF RESPONSIBILITY):**

            *   **Data Elements:**
                *   Quay account number: Stating the quay account number replaces the conventional declaration of responsibility and is obligatory when storage fees are incurred and no declaration of responsibility has been submitted.
                *   Purpose: Purpose as a reference for charges made to the quay account. This information must be provided if a quay account number is quoted.

            *   **Status Codes:**
                *   **109 Please provide quay account number:** This indicates that a quay account number must be provided when the free storage period comes to an end.
                *   **606 Quay account number required:** Storage fees are already payable which are not being borne by the container operator.
                *   **607 Quay account number is blocked:** The quay account number provided is blocked.
                *   **608 Quay account number is unknown:** The terminal does not recognise the quay account number provided.

    *   **3.2.3 Empty Depot/Depot Incoming:** Only applies to empty containers.

        *   **Data Elements:**
                *   Container number: Prefix + 7-digit number, same as the number on the container
                *   ISO code: ISO code in accordance with UN ISO6346
                *   Carrier code: Container operator according to the DAKOSY code list

            *   **Status Codes:**
                *   **100 OK:** The pre-announcement is correct; all prerequisites for self- service terminal handling with the pre-announcement number (PAN) have been met.
                *   **200 Bring documents:** As part of processing, a manual stage is required in the pre-check. Full transport documentation including the turn-in reference must be presented.
                *   **620 Carrier code unknown:** The terminal does not recognise the carrier code (shipping company) provided. This means: 1. The terminal uses a different code from the DAKOSY key list for the shipping company. 2. The shipping company is not at the terminal.
                *   **626 Empty container delivery not permitted for shipping company:** The terminal does not accept empty containers for the shipping company specified.

    *   **3.2.4 Empty Depot/Depot Outgoing:** Only applies to empty containers.

        *   **NON-NUMERIC COLLECTION OF EMPTY CONTAINERS:**

            *   **Data Elements:**
                *   ISO code: The group ISO code in accordance with UN ISO6346. The ISO code from the release must either be identical or come under this group code.
                *   Release reference: Release number (often called MT collection reference on transport documents).

            *   **Status Codes:**
                *   **100 OK:** The pre-announcement is correct; all prerequisites for self- service terminal handling with the pre-announcement number (PAN) have been met.
                *   **601 No or unknown release:** The terminal does not have a release under the reference provided.
                *   **603 Release complete:** The number/contingent of released containers has already been delivered.
                *   **604 Wrong container type for release:** The ISO code provided does not match the ISO code in the release from the shipping company.

        *   **NUMERIC COLLECTION OF EMPTY CONTAINERS:**

            *   **Data Elements:**
                *   Container number: Prefix + 7-digit number, same as the number on the container
                *   Release reference: Release number or MT collection reference according to transport documents.

            *   **Status Codes:**
                *   **100 OK:** The pre-announcement is correct; all prerequisites for self- service terminal handling with the pre-announcement number (PAN) have been met.
                *   **310 Container not yet in stock:** The terminal system recognises the container but it is not yet physically at the terminal.
                *   **601 No or unknown release:** The terminal does not have a release for the container.
                *   **602 Wrong release or authentication reference:** The release reference does not match the information provided by the shipping company.
                *   **611 Container currently unknown:** The terminal does not recognise the container, nor is it expected.
                *   **660 Container transport already scheduled:** A pre-announcement already exists for the container or the container has been assigned to another carrier.
                *   **670 Container blocked by terminal:** The container has not been released by the terminal.

*   **3.3 Special Containers:** Planned arrival time always needed for slot booking.

    *   **3.3.1 Reefer:**

        *   **Additional Data Element:**
            *   Non-operating reefers: If the ISO code indicates it is a reefer container (third character is “R” or “T”), please also state on delivery (Y/N) whether the reefer should be operating at the terminal or not.

            *   **Status Codes:**
                *   **100 OK:** All prerequisites for self-service terminal handling with the pre-announcement number (PAN) have been met (CTA collection only).
                *   **200 Bring documents:** As part of processing, a manual stage is required in the pre-check. Full transport documentation including temperature specifications must be presented on delivery.

    *   **3.3.2 OOG Containers:**

        *   **Additional Data Element:**
            *   Oversize: Specifies (Y/N) if the container (including cargo) is oversize.

            *   **Status Code:**
                *   **200 Bring documents:** As part of processing, a manual stage is required in the pre-check. Full transport documentation including the oversize dimensions must be presented.

    *   **3.3.3 Hazardous Cargo:**

        *   **Additional Data Element:**
            *   Hazardous cargo: Specifies (Y/N) if a container contains hazardous cargo.

            *   **Status Code:**
                *   **200 Bring documents:** As part of processing, a manual stage is required in the pre-check. Depending on the hazardous cargo, the relevant documents must be presented in full.

*   **3.4 Special Cases:**

    *   **3.4.1 CUSTOMS – NCTS TRANSIT PROCEDURE (T1):**

        *   **Additional Data Elements:**
            *   T1 indicator: Indication (Y/N) of whether the NCTS transit procedure T1 is relevant for the container.
            *   MRN numbers: The relevant MRN numbers must be provided for T1- relevant deliveries.
            *   Position numbers: The included position numbers for each MRN must be provided for T1-relevant deliveries.
            *   Number of packages: The total number of packages must be provided for T1- relevant collections.

            *   **Status Codes:**
                *   **210 Check customs opening hours:** As part of processing, at least one manual stage is required in the pre-check. The driver must go to the manual pre-check and/or customs area at the terminal for processing. The papers required for the T1 transit procedure must be presented.
                *   **551 In custody:** Terminal is being held in custody by customs. If the container is to be collected under the NCTS transit procedure, “T1” must be specified.

    *   **3.4.2 KLV Rail (Land–Land Transport):** Pre-announcement not currently available. Processed without pre-announcement in MPC. The relevant transport documents must be presented.

    *   **3.4.3 Inspection (customs, veterinary office):** Pre-announcement not available. Processed without pre-announcement in the MPC. The relevant transport documents must be presented.

    *   **3.4.4 Packing Facility (CTB):** Pre-announcement not currently available for packing facility at the CTB. Processed without the pre-announcement in the MPC. The relevant transport documents must be presented.

    *   **3.4.5 Collection of an Export Container:** Pre-announcement not currently available for export containers that are already at the terminal and that must be collected again. Processed without the pre-announcement in the MPC. The relevant transport documents must be presented.

## 4. Slot-booking process (Section 4)

*   **4.1 Introduction:** Slots mandatory for all container transport subject to mandatory pre-announcement (see 3.1). A valid time window is needed before processing can be carried out at the terminal. The obligation to pre-book a slot applies at all times during the terminals’ advertised opening hours.

*   **4.2 Pre-announcement and Slot Booking:**
    *   **(4.2.1 General Approach):**
        *   Slot booking based on mandatory TR02 pre-announcement.
        *   TR02 messages include scheduled transport time (arrival time) stipulated by dispatcher or driver.
        *   Time assigned a 1-hour time window, beginning on the hour.
        *   Terminals pre-determine slot capacities per hour based on resources.
        *   Slots assigned first-come, first-served.
        *   No slots at preferred time = negative response, system offers alternatives before/after.
        *   Terminal capacity utilization viewable at https://slot.truckgate.de. Interface to import capacity utilization status available at www.truckgate.de.
        *   Slots bookable up to three (3) working days in advance.
        *   Recommend off-peak times (evening hours) for easier slot booking and faster handling due to lower terminal utilization.
        *   Slot bookings invalid after handling time window expires (leeway period for Priority 2).
        *   Unused pre-announcements are cancelled automatically by the terminal after twelve hours.

    *   **(4.2.2 Special Regulations):**
        *   Export containers: slot pre-booking possible without container number (initial status “not executable”, container number added later = “executable” & PAN).
        *   Containers not yet unloaded from ship: pre-announcement “executable” automatically when container ready, PAN sent.
        *   MT deliveries: slot booking possible without container number.
        *   Slot booking also applies to large-capacity/heavy-duty transports. MPC handling for trucks with approvals and non-compliant booked slots.

*   **4.3 Handling:**

    *   Truck arrival at terminal: driver presents trucker card to OCR reader, enters PAN (OCR gate).
    *   Arrival time compared to booked slot, handling priority determined.

    *   **Priority Handling with Slot Booking:**
        *   **Priority 1 (On Time):** Arrival within 60-minute slot +/- 30 minutes leeway = Priority 1, processed on schedule.
        *   **Priority 2 (Extended Leeway):** If agreed time window missed, rebook before arrival. Processing within extended leeway (+/- additional 60 mins) if capacity allows (check https://slot.truckgate.de).
        *   **Priority 3 (Outside Leeway):** Deviation > 90 mins from booked slot = slot must be rebooked before arrival, truck not cleared otherwise.
        *   No slot booking possible at terminal. No waiting allowed in terminal parking area.
        *   MPC Slot Validation: Slot validation at MPC via slot ticket column, receipt with priority presented during MPC.

*   **4.4 Changing Slots:**
    *   **(4.4.1 Adding to Bookings):** Adding containers to existing pre-announcement possible at short notice (even if slot fully booked) if pre-announcement and added container status request are “executable”.
    *   **(4.4.2 Cancelling Slots):** Slots cancellable at short notice. Timely cancellation (at least 4 hours before time window start) recommended. High no-show quota in a week = limited peak-time slots next week (off-peak still possible).

*   **4.5 Exceptions:**
    *   **SUSPENDING SLOT COMPLIANCE:** Terminals can suspend slot booking process when necessary (e.g., prolonged access issues). Trucks handled outside booked slots during suspension periods (check https://slot.truckgate.de). All trucks with slots during suspension processed upon arrival, even if late. Slot compliance can be lifted for certain transport types based on slot classes (Priority 1 handling for special slot classes).

    *   **SLOT CLASSES:** Priority 1 irrespective of punctuality for:
        *   Delivery of IMO containers with dangerous goods categories 1.1, 1.2 and 7 (IMOANM slot class)
        *   Delivery of late arrivals notified by shipping company (LATE slot class)
        *   Delivery and receipt of containers in ship repositioning (SHIP slot class)
        *   Special slot classes set up by terminals and bookable by hauliers after HHLA go-ahead. Specify special slot class in TR02 pre-announcement. Misuse may restrict TR02 use.

*   **4.6 TRANSPORT MOVEMENTS WITHOUT SLOT BOOKINGS:** Slots mandatory EXCEPT special cases (3.4.2-3.4.5: Rail, Inspection, CTB Packing Facility, Export Container Collection). If TR02 pre-announcement impossible, driver registers via manual pre-check (MPC), processed without PAN.

*   **4.7 THE THREE GOLDEN RULES (REITERATED):**
    1.  Never arrive without slot booking or with major arrival time deviation (Priority 3).
    2.  Arrive within booked time window (Priority 1). Priority 2 handling depends on terminal capacity.
    3.  Cancel slot promptly (at least before time window start) if unable to make it.

---