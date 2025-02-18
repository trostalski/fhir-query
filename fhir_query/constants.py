DF_DEFAULT_COLUMNS = {
    "Patient": {
        "resourceType": "resourceType",
        "id": "id",
        "firstname": "name[0].given[0]",
        "lastname": "name[0].family",
        "gender": "gender",
        "birthdate": "birthDate",
        "street": "address[0].line[0]",
        "city": "address[0].city",
        "state": "address[0].state",
    },
    "Condition": {
        "resourceType": "resourceType",
        "id": "id",
        "category": "category[0].coding[0].display",
        "display": "code.coding[0].display",
        "code": "code.coding[0].code",
        "system": "code.coding[0].system",
        "subject": "subject.reference",
        "encounter": "encounter.reference",
        "date": "recordedDate",
    },
    "Observation": {
        "resourceType": "resourceType",
        "id": "id",
        "category": "category[0].coding[0].display",
        "display": "code.coding[0].display",
        "code": "code.coding[0].display",
        "system": "code.coding[0].system",
        "value": "valueQuantity.value",
        "unit": "valueQuantity.unit",
        "subject": "subject.reference",
        "encounter": "encounter.reference",
        "date": "effectiveDateTime",
    },
    "DiagnosticReport": {
        "resourceType": "resourceType",
        "id": "id",
        "title": "presentedForm[0].title",
        "url": "presentedForm[0].attachment.url",
        "contentType": "presentedForm[0].contentType",
        "category": "category[0].coding[0].display",
        "subject": "subject.reference",
        "encounter": "encounter.reference",
        "date": "effectiveDateTime",
    },
    "Medication": {
        "resourceType": "resourceType",
        "id": "id",
        "display": "code.coding[0].display",
        "code": "code.coding[0].code",
        "system": "code.coding[0].system",
        "manufacturer": "manufacturer.display",
    },
    "MedicationRequest": {
        "resourceType": "resourceType",
        "id": "id",
        "medication": "medicationReference.reference",
        "status": "status",
        "subject": "subject.reference",
    },
    "MedicationAdministration": {
        "resourceType": "resourceType",
        "id": "id",
        "medication": "medicationReference.reference",
        "status": "status",
        "subject": "subject.reference",
        "effectiveDateTime": "effectiveDateTime",
        "dosageText": "dosage.text",
    },
    "MedicationStatement": {
        "resourceType": "resourceType",
        "id": "id",
        "medication": "medicationReference.reference",
        "status": "status",
        "subject": "subject.reference",
        "dateAsserted": "dateAsserted",
        "dosageText": "dosage[0].text",
    },
    "Location": {
        "resourceType": "resourceType",
        "id": "id",
        "description": "description",
        "status": "status",
        "partOf": "partOf.reference",
    },
}
