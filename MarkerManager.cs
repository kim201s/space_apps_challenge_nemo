using System.Collections.Generic;
using UnityEngine;


//Structure
public struct MarkerSpot
{
    public GameObject markerSpot;
    public double latitude;
    public double longitude;
}
public class MarkerManager : MonoBehaviour, IMarkerManager
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private Transform _earth;
    
    public MarkerSpot NewMarkerSpot { set{SetMarkerParent(value);} }

    
    
    
    private List<MarkerSpot> _markerSpots = new();


    private void Start()
    {
        _earth = ServiceLocator.Current.Get<GetTheEarth>().Earth;
    }


    private void SetMarkerParent(MarkerSpot Spot)
    {
        
        Spot.markerSpot.transform.SetParent(_earth);
        _markerSpots.Add(Spot);

    }
    
    private void Update()
    {
       
    }
    



}
