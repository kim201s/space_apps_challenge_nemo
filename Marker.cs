using System;
using UnityEngine;
using UnityEngine.UIElements;

[DefaultExecutionOrder(-997)]
public class Marker : MonoBehaviour, IMarker
{

    
    Transform _earth;

    
  
    [SerializeField] private Material _fireSpot;

    readonly float  MATHCING_EARTH_SCALE = 40.5f;
    readonly float scaleMarker = 1f;
    
   

    //Main values
    double lat;
    double lon;
    

    private void Start()
    {
        
    }
   

    public void ApplySpot(double latitude, double longitude)
    {
        
        _earth = ServiceLocator.Current.Get<GetTheEarth>().Earth;

        //Get Radius
        float radius = _earth.localScale.x/2;


        lat = GetRad(latitude);
        lon = GetRad(longitude);


        GameObject MarkerObject = CreateVisualMarker();
        CalculateMarkerPosition(MarkerObject ,radius);

        //Apply material - made by shader Graph 
        MarkerObject.GetComponent<MeshRenderer>().material = _fireSpot;

        //Storing nessacery values
        MarkerSpot spot = new MarkerSpot();

        spot.markerSpot = MarkerObject;
        spot.latitude = latitude;
        spot.longitude = longitude;

        Debug.Log("Coor: lat " + latitude  + " lon " + longitude);

        //Store the structure
        ServiceLocator.Current.Get<IMarkerManager>().NewMarkerSpot = spot;
    }

    // public void CalculatePosition()
    // {
    //     float radius = _earth.localScale.x/2;
    //     if(_storedRadius != radius)
    //     CalculateMarkerPosition(radius);

        
    // }

    private GameObject CreateVisualMarker()
    {
        return GameObject.CreatePrimitive(
            PrimitiveType.Sphere
        );
    }

    private double GetRad(double value) => value * Math.PI / 180f;

    private void CalculateMarkerPosition(GameObject markerSpot ,float radius)
    {
        //convert lat and lon to Vector3
        double x = radius * Math.Cos(lat) * Math.Cos(lon);
        double y = radius * Math.Sin(lat);
        double z = radius * Math.Cos(lat) * Math.Sin(lon);

        //apply calculation
        Vector3 position = new Vector3((float)x, (float)y, (float)z);
        markerSpot.transform.position = position * MATHCING_EARTH_SCALE;
        markerSpot.transform.localScale = Vector3.one * scaleMarker;

       
    }


    
}
